import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, List, Tuple

import easyocr  # type: ignore

from taikoi2t.application.modal import find_modal
from taikoi2t.application.student import (
    StudentDictionary,
    preprocess_students_for_ocr,
    recognize_student,
    recognize_student_by_character,
)
from taikoi2t.application.wins import check_player_wins
from taikoi2t.implements.image import (
    convert_to_grayscale,
    get_roi_bbox,
    new_image_meta,
    read_image,
    show_bboxes,
)
from taikoi2t.implements.match import get_match_id
from taikoi2t.implements.ocr import read_text_from_roi
from taikoi2t.implements.settings import Settings
from taikoi2t.implements.team import new_team_from, sort_specials
from taikoi2t.models.args import VERBOSE_IMAGE, VERBOSE_PRINT
from taikoi2t.models.column import Requirement
from taikoi2t.models.image import Image, RelativeBox
from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student
from taikoi2t.models.team import Team

logger: logging.Logger = logging.getLogger("taikoi2t.match")

__PLAYER_NAME_RELATIVE = RelativeBox(left=6 / 19, top=1 / 7, right=1 / 2, bottom=1 / 5)
__OPPONENT_NAME_RELATIVE = RelativeBox(left=5 / 6, top=1 / 7, right=1, bottom=1 / 5)


def extract_match_result_from_path(
    path: Path,
    dictionary: StudentDictionary,
    reader: easyocr.Reader,
    settings: Settings,
) -> MatchResult | None:
    image_process_starts_at = datetime.now()
    path_str = path.as_posix()
    match_id: str = get_match_id(time.time_ns(), path.name)
    logger.info(f"=== START: {path_str}; id: {match_id} ===")

    if not path.exists():
        logger.error(f"{path_str} is not found")
        return None
    if not path.is_file():
        logger.error(f"{path_str} is not a file")
        return None

    source = read_image(path)
    if source is None:
        logger.error(f"{path_str} cannot read as an image")
        return None

    match_result = extract_match_result(
        match_id, path, source, dictionary, reader, settings
    )

    logger.info(f"{path_str} => {match_result}")
    logger.info(
        f"=== END: {path_str}; id: {match_id}, elapsed: {datetime.now() - image_process_starts_at} ==="
    )

    return match_result


def extract_match_result(
    match_id: str,
    image_path: Path,
    source: Image,
    dictionary: StudentDictionary,
    reader: easyocr.Reader,
    settings: Settings,
) -> MatchResult | None:
    image_path_str = image_path.as_posix()
    grayscale = convert_to_grayscale(source)  # for OCR
    if grayscale is None:
        return None

    modal = find_modal(grayscale, settings.verbose)
    if modal is None:
        logger.error(f"Cannot detect any result-box in {image_path_str}")
        return None
    if settings.verbose >= VERBOSE_IMAGE:
        show_bboxes(source, [modal])

    player_team: Team
    opponent_team: Team

    def process_students() -> Tuple[Team, Team] | None:
        preprocessed_images = preprocess_students_for_ocr(grayscale, modal)
        if len(preprocessed_images) == 0:
            return None

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
        process_students, "students", image_path_str, settings
    ) or (new_team_from([]), new_team_from([]))

    if settings.sp_sort:
        # overwrite specials
        player_team.specials = sort_specials(player_team.specials)
        opponent_team.specials = sort_specials(opponent_team.specials)
        logger.info(f"--- DONE sp_sort ({image_path_str}) ---")
    else:
        logger.info(f"--- SKIP sp_sort ({image_path_str}) ---")

    # passes colored source image because checking win or lose uses mean saturation of the region
    player_wins = __run_process(
        lambda: check_player_wins(source, modal),
        "win_or_lose",
        image_path_str,
        settings,
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
        image_path_str,
        settings,
    )

    # overwrite owner
    opponent_team.owner = __run_process(
        lambda: read_text_from_roi(
            reader, grayscale, get_roi_bbox(modal, __OPPONENT_NAME_RELATIVE)
        ),
        "opponent",
        image_path_str,
        settings,
    )

    image_height, image_width = source.shape[:2]
    image_meta = new_image_meta(image_path, (image_width, image_height), modal)
    return MatchResult(match_id, image_meta, player=player_team, opponent=opponent_team)


def __run_process[Ret](
    process: Callable[[], Ret],
    requirement: Requirement,
    image_path_str: str,
    settings: Settings,
) -> Ret | None:
    if requirement in settings.requirements:
        starts_at = datetime.now()
        logger.info(f"--- START {requirement} ({image_path_str}) ---")

        result: Ret = process()

        logger.info(
            f"--- END {requirement} ({image_path_str}); elapsed: {datetime.now() - starts_at} ---"
        )
        return result
    else:
        if settings.verbose >= VERBOSE_PRINT:
            logger.info(f"--- SKIP {requirement} ({image_path_str}) ---")
        return None
