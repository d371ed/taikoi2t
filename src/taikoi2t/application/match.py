import sys
from datetime import datetime
from typing import Callable, List, Tuple

import cv2
import easyocr  # type: ignore

from taikoi2t.application.modal import find_modal
from taikoi2t.application.student import StudentDictionary, extract_student_names
from taikoi2t.application.wins import check_player_wins
from taikoi2t.implements.image import get_roi_bbox, show_image
from taikoi2t.implements.ocr import read_text_from_roi
from taikoi2t.implements.settings import Settings
from taikoi2t.implements.team import new_team_from, sort_specials
from taikoi2t.models.args import VERBOSE_ERROR, VERBOSE_IMAGE, VERBOSE_PRINT
from taikoi2t.models.column import Requirement
from taikoi2t.models.image import Image, ImageMeta, RelativeBox
from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student
from taikoi2t.models.team import Team

__PLAYER_NAME_RELATIVE = RelativeBox(left=6 / 19, top=1 / 7, right=1 / 2, bottom=1 / 5)
__OPPONENT_NAME_RELATIVE = RelativeBox(left=5 / 6, top=1 / 7, right=1, bottom=1 / 5)


def extract_match_result(
    source: Image,
    image_meta: ImageMeta,
    dictionary: StudentDictionary,
    reader: easyocr.Reader,
    settings: Settings,
) -> MatchResult | None:
    # for OCR
    grayscale: Image = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)

    modal = find_modal(grayscale, settings.verbose)
    if modal is None:
        if settings.verbose >= VERBOSE_ERROR:
            print(
                f"ERROR: Cannot detect any result-box in {image_meta.path}",
                file=sys.stderr,
            )
        return None
    if settings.verbose >= VERBOSE_IMAGE:
        show_image(
            cv2.rectangle(
                source.copy(),
                (modal.left, modal.top),
                (modal.right, modal.bottom),
                (0, 255, 0),
            ),
            "modal",
        )

    player_team: Team
    opponent_team: Team

    def process_students() -> Tuple[Team, Team] | None:
        extracted_student_names = extract_student_names(
            reader,
            grayscale,
            modal,
            dictionary.allow_char_list,
            settings.verbose,
        )

        if len(extracted_student_names) < 12:
            if settings.verbose >= VERBOSE_ERROR:
                print(
                    f"ERROR: Student's names extraction error. len: {len(extracted_student_names)}",
                    file=sys.stderr,
                )
            return None

        # matching student's names with the dictionary
        students: List[Student] = [
            dictionary.match(detected, settings.verbose)
            for detected in extracted_student_names
        ]

        return new_team_from(students[0:6]), new_team_from(students[6:12])

    player_team, opponent_team = __run_process(
        process_students, "students", image_meta, settings
    ) or (new_team_from([]), new_team_from([]))

    if settings.sp_sort:
        # overwrite specials
        player_team.specials = sort_specials(player_team.specials)
        opponent_team.specials = sort_specials(opponent_team.specials)
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- DONE sp_sort ({image_meta.path}) ---")
    else:
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- SKIP sp_sort ({image_meta.path}) ---")

    # passes colored source image because checking win or lose uses mean saturation of the region
    player_wins = __run_process(
        lambda: check_player_wins(source, modal), "win_or_lose", image_meta, settings
    )
    if player_wins is not None:
        # overwrite wins
        player_team.wins = player_wins
        opponent_team.wins = not player_wins

    # overwrite owner
    player_team.owner = __run_process(
        lambda: read_text_from_roi(
            reader, grayscale, get_roi_bbox(modal, __PLAYER_NAME_RELATIVE)
        ),
        "player",
        image_meta,
        settings,
    )

    # overwrite owner
    opponent_team.owner = __run_process(
        lambda: read_text_from_roi(
            reader, grayscale, get_roi_bbox(modal, __OPPONENT_NAME_RELATIVE)
        ),
        "opponent",
        image_meta,
        settings,
    )

    updated_image_meta = ImageMeta(
        image_meta.path,
        image_meta.name,
        width=image_meta.width,
        height=image_meta.height,
        modal=modal,
    )
    return MatchResult(updated_image_meta, player=player_team, opponent=opponent_team)


def __run_process[Ret](
    process: Callable[[], Ret],
    requirement: Requirement,
    image_meta: ImageMeta,
    settings: Settings,
) -> Ret | None:
    if requirement in settings.requirements:
        starts_at = datetime.now()
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- START {requirement} ({image_meta.path}) ---")

        result: Ret = process()

        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- END {requirement} ({image_meta.path}) ---")
            ends_at = datetime.now()
            print(
                f"    start: {starts_at}, end: {ends_at}, elapsed: {ends_at - starts_at}"
            )
        return result
    else:
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- SKIP {requirement} ({image_meta.path}) ---")
        return None
