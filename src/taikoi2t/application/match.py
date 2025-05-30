import logging
from datetime import datetime
from typing import Callable, Iterable, List, Tuple

import cv2
import easyocr  # type: ignore

from taikoi2t.application.modal import find_modal
from taikoi2t.application.student import (
    StudentDictionary,
    preprocess_students_for_ocr,
    recognize_student,
    recognize_student_by_character,
)
from taikoi2t.application.wins import check_player_wins
from taikoi2t.implements.image import get_roi_bbox, show_image
from taikoi2t.implements.ocr import read_text_from_roi
from taikoi2t.implements.settings import Settings
from taikoi2t.implements.team import new_team_from, sort_specials
from taikoi2t.models.args import VERBOSE_IMAGE, VERBOSE_PRINT
from taikoi2t.models.column import Requirement
from taikoi2t.models.image import Image, ImageMeta, RelativeBox
from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student
from taikoi2t.models.team import Team

logger: logging.Logger = logging.getLogger("taikoi2t.match")

__PLAYER_NAME_RELATIVE = RelativeBox(left=6 / 19, top=1 / 7, right=1 / 2, bottom=1 / 5)
__OPPONENT_NAME_RELATIVE = RelativeBox(left=5 / 6, top=1 / 7, right=1, bottom=1 / 5)


def extract_match_result(
    source: Image,
    image_meta: ImageMeta,
    dictionary: StudentDictionary,
    reader: easyocr.Reader,
    settings: Settings,
) -> MatchResult | None:
    grayscale: Image = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)  # for OCR

    modal = find_modal(grayscale, settings.verbose)
    if modal is None:
        logger.error(f"Cannot detect any result-box in {image_meta.path}")
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
        preprocessed_images = preprocess_students_for_ocr(grayscale, modal)

        first_recognized_students: Iterable[Student] = [
            recognize_student(reader, dictionary, image, settings.verbose)
            for image in preprocessed_images
        ]

        second_recognized_students: List[Student] = []
        for index, (image, first_recognized) in enumerate(
            zip(preprocessed_images, first_recognized_students)
        ):
            second_recognized: Student = first_recognized
            if first_recognized.is_error:
                logger.info(
                    f"!! Recognition error at {index}. Retrying it by single character."
                )
                second_recognized = recognize_student_by_character(
                    reader, dictionary, image, settings.verbose
                )
            second_recognized_students.append(second_recognized)

        return (
            new_team_from(second_recognized_students[0:6]),
            new_team_from(second_recognized_students[6:12]),
        )

    player_team, opponent_team = __run_process(
        process_students, "students", image_meta, settings
    ) or (new_team_from([]), new_team_from([]))

    if settings.sp_sort:
        # overwrite specials
        player_team.specials = sort_specials(player_team.specials)
        opponent_team.specials = sort_specials(opponent_team.specials)
        logger.info(f"--- DONE sp_sort ({image_meta.path}) ---")
    else:
        logger.info(f"--- SKIP sp_sort ({image_meta.path}) ---")

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
        logger.info(f"--- START {requirement} ({image_meta.path}) ---")

        result: Ret = process()

        logger.info(
            f"--- END {requirement} ({image_meta.path}); elapsed: {datetime.now() - starts_at} ---"
        )
        return result
    else:
        if settings.verbose >= VERBOSE_PRINT:
            logger.info(f"--- SKIP {requirement} ({image_meta.path}) ---")
        return None
