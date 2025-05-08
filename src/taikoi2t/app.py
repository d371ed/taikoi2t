import csv
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List, Sequence, Tuple

import cv2
import easyocr  # type: ignore

from taikoi2t.implements.args import (
    parse_args,
    validate_args,
)
from taikoi2t.implements.image import (
    cutout_image,
    level_contrast,
    resize_to,
    show_image,
    skew,
)
from taikoi2t.implements.match import (
    new_errored_match_result,
    render_match,
)
from taikoi2t.implements.ocr import Character, join_chars
from taikoi2t.implements.settings import Settings, new_settings_from
from taikoi2t.implements.student import (
    Student,
    StudentDictionary,
    normalize_student_name,
)
from taikoi2t.implements.team import new_team_from, sort_specials
from taikoi2t.models.args import VERBOSE_ERROR, VERBOSE_IMAGE, VERBOSE_PRINT
from taikoi2t.models.image import BoundingBox, Image, ImageMeta
from taikoi2t.models.match import MatchResult
from taikoi2t.models.run import RunResult
from taikoi2t.models.team import Team


def run(argv: Sequence[str] | None = None) -> None:
    run_starts_at = datetime.now()
    run_result = RunResult(
        arguments=list(argv or sys.argv),
        starts_at=run_starts_at.isoformat(),
        ends_at="",
        matches=[],
    )

    args = parse_args(run_result.arguments)
    if args.verbose >= VERBOSE_PRINT:
        print(args)
    validate_args(args)

    settings = new_settings_from(args)
    if settings.verbose >= VERBOSE_PRINT:
        print(settings)

    student_alias_pairs = read_dictionary_source_file(args.dictionary)
    if student_alias_pairs is None:
        print(
            f"FATAL: {args.dictionary.as_posix()} is invalid as student's dictionary",
            file=sys.stderr,
        )
        sys.exit(1)

    student_dictionary = StudentDictionary(student_alias_pairs)

    if settings.verbose >= VERBOSE_PRINT:
        print(student_dictionary.allow_char_list)

    reader = easyocr.Reader(["ja", "en"], verbose=settings.verbose >= VERBOSE_PRINT)

    def append_match_result(match_result: MatchResult) -> None:
        run_result.matches.append(match_result)
        if settings.output_format != "json":
            print(render_match(match_result, settings))

    for path in args.files:
        image_process_starts_at = datetime.now()
        if settings.verbose >= VERBOSE_PRINT:
            print(f"=== START: {path.as_posix()} ===")

        image_meta = ImageMeta(path.as_posix(), path.name)
        if not path.exists():
            if settings.verbose >= VERBOSE_ERROR:
                print(f"ERROR: {path.as_posix()} is not found", file=sys.stderr)
            append_match_result(new_errored_match_result(image_meta))
            continue

        # imread returns None when error occurred
        source: Image | None = cv2.imread(path.as_posix())
        if source is None:  # type: ignore
            if settings.verbose >= VERBOSE_ERROR:
                print(
                    f"ERROR: {path.as_posix()} cannot read as an image", file=sys.stderr
                )
            append_match_result(new_errored_match_result(image_meta))
            continue

        # overwrite dimensions
        image_meta.height, image_meta.width, _ = source.shape
        if settings.verbose >= VERBOSE_PRINT:
            print(image_meta)

        match_result = extract_match_result(
            source, image_meta, student_dictionary, reader, settings
        ) or new_errored_match_result(image_meta)
        if args.verbose >= VERBOSE_PRINT:
            print(match_result)
        append_match_result(match_result)

        if settings.verbose >= VERBOSE_PRINT:
            image_process_ends_at = datetime.now()
            print(f"=== END: {path.as_posix()} ===")
            print(
                f"    start: {image_process_starts_at}, end: {image_process_ends_at}, elapsed: {image_process_ends_at - image_process_starts_at}"
            )

    run_ends_at = datetime.now()
    run_result.ends_at = run_ends_at.isoformat()
    if settings.verbose >= VERBOSE_PRINT:
        print("=== RUN FINISHED ===")
        print(
            f"    start: {run_result.starts_at}, end: {run_result.ends_at}, elapsed: {run_ends_at - run_starts_at}"
        )

    if settings.output_format == "json":
        print(json.dumps(asdict(run_result), ensure_ascii=False))


def read_dictionary_source_file(path: Path) -> List[Tuple[str, str]] | None:
    rows: List[Tuple[str, str]]
    with path.open(mode="r", encoding="utf-8") as students_file:
        try:
            rows = [
                (row[0], row[1] if len(row) >= 2 else "")
                for row in csv.reader(students_file)
            ]
        except IndexError:
            return None
    if len(rows) == 0:
        return None
    return rows


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
    if "students" in settings.requirements:
        starts_at = datetime.now()
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- START students ({image_meta.path}) ---")

        detected_student_names = detect_student_names(
            reader,
            grayscale,
            modal,
            dictionary.allow_char_list,
            settings.verbose,
        )

        if len(detected_student_names) < 12:
            if settings.verbose >= VERBOSE_ERROR:
                print(
                    f"ERROR: Student's names detection error. len: {len(detected_student_names)}",
                    file=sys.stderr,
                )
            return None

        # matching student's names with the dictionary
        students: List[Student] = [
            dictionary.match(detected, settings.verbose)
            for detected in detected_student_names
        ]

        player_team = new_team_from(students[0:6])
        opponent_team = new_team_from(students[6:12])

        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- END students ({image_meta.path}) ---")
            ends_at = datetime.now()
            print(
                f"    start: {starts_at}, end: {ends_at}, elapsed: {ends_at - starts_at}"
            )
    else:
        player_team = new_team_from([])
        opponent_team = new_team_from([])
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- SKIP students ({image_meta.path}) ---")

    if settings.sp_sort:
        # overwrite
        player_team.specials = sort_specials(player_team.specials)
        opponent_team.specials = sort_specials(opponent_team.specials)
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- DONE sp_sort ({image_meta.path}) ---")
    else:
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- SKIP sp_sort ({image_meta.path}) ---")

    if "win_or_lose" in settings.requirements:
        starts_at = datetime.now()
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- START win_or_lose ({image_meta.path}) ---")

        # passes colored source image because checking win or lose uses mean saturation of the area
        # overwrite
        player_team.wins = check_player_wins(source, modal)
        opponent_team.wins = not player_team.wins

        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- END win_or_lose ({image_meta.path}) ---")
            ends_at = datetime.now()
            print(
                f"    start: {starts_at}, end: {ends_at}, elapsed: {ends_at - starts_at}"
            )
    else:
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- SKIP win_or_lose ({image_meta.path}) ---")

    if "opponent" in settings.requirements:
        starts_at = datetime.now()
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- START opponent ({image_meta.path}) ---")

        opponent_team.owner = detect_opponent(reader, grayscale, modal)  # overwrite

        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- END opponent ({image_meta.path}) ---")
            ends_at = datetime.now()
            print(
                f"    start: {starts_at}, end: {ends_at}, elapsed: {ends_at - starts_at}"
            )
    else:
        if settings.verbose >= VERBOSE_PRINT:
            print(f"--- SKIP opponent ({image_meta.path}) ---")

    updated_image_meta = ImageMeta(
        image_meta.path,
        image_meta.name,
        width=image_meta.width,
        height=image_meta.height,
        modal=modal,
    )
    return MatchResult(updated_image_meta, player=player_team, opponent=opponent_team)


def find_modal(grayscale: Image, verbose: int = 0) -> BoundingBox | None:
    RESULT_ASPECT_RATIO: float = 2.33
    ASPECT_RATIO_EPS: float = 0.05
    APPROX_PRECISION: float = 0.03

    source_width: int = grayscale.shape[1]

    binary: Image = cv2.threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    preview: Image | None = None
    if verbose >= VERBOSE_IMAGE:
        preview = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    result: BoundingBox | None = None
    for contour in contours:
        epsilon: float = APPROX_PRECISION * cv2.arcLength(contour, True)  # type: ignore
        approx = cv2.approxPolyDP(contour, epsilon, True)  # type: ignore
        rect: List[int] = cv2.boundingRect(approx)  # type: ignore

        [left, top, width, height] = rect
        if preview is not None:
            cv2.drawContours(preview, [approx], -1, (0, 0, 255))

        aspect_ratio: float = width / height
        if (
            width > source_width / 2
            and abs(aspect_ratio - RESULT_ASPECT_RATIO) < ASPECT_RATIO_EPS
        ):
            result = BoundingBox(left, top, left + width, top + height)

    if preview is not None:
        show_image(preview)

    return result


def detect_student_names(
    reader: easyocr.Reader,
    grayscale: Image,
    modal: BoundingBox,
    char_allow_list: str,
    verbose: int = 0,
) -> List[str]:
    student_name_images = __preprocess_students(grayscale, modal)

    results: List[str] = list()
    for image in student_name_images:
        chars: List[Character] = reader.readtext(  # type: ignore
            image, allowlist=char_allow_list, mag_ratio=2
        )  # type: ignore

        if verbose >= VERBOSE_PRINT:
            print([char[1] for char in chars])
        if verbose >= VERBOSE_IMAGE:
            for char in chars:
                top_left, _, bottom_right, _ = char[0]
                cv2.rectangle(image, top_left, bottom_right, (0, 0, 0))
            show_image(image)

        name = normalize_student_name(join_chars(chars))
        results.append(name)
    return results


def __preprocess_students(grayscale: Image, modal: BoundingBox) -> List[Image]:
    WIDTH: int = 4000

    FOOTER_RATIO: float = 0.085
    footer_height = int(FOOTER_RATIO * modal.height)
    footer_top = int(modal.bottom - footer_height)
    footer_area = BoundingBox(
        left=modal.left, top=footer_top, right=modal.right, bottom=modal.bottom
    )

    footer = cutout_image(grayscale, footer_area)
    resized = resize_to(footer, WIDTH)
    skewed = skew(resized, 14.0)
    leveled = level_contrast(skewed, 112, 192)

    # cut out 12 sections
    PITCH_RATIO: float = 113 / 1844
    PITCH: int = int(WIDTH * PITCH_RATIO)
    TEAM_WIDTH: int = PITCH * 6
    PLAYER_TEAM_LEFT: int = 216
    OPPONENT_TEAM_LEFT: int = WIDTH // 2 + 292
    height: int = leveled.shape[1]

    results: List[Image] = list()
    for x in range(PLAYER_TEAM_LEFT, PLAYER_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(cutout_image(leveled, BoundingBox(x, 0, (x + PITCH), height)))
    for x in range(OPPONENT_TEAM_LEFT, OPPONENT_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(cutout_image(leveled, BoundingBox(x, 0, (x + PITCH), height)))

    return results


def check_player_wins(source: Image, modal: BoundingBox) -> bool:
    target = BoundingBox(
        left=modal.width // 12 + modal.left,
        top=modal.height // 5 + modal.top,
        right=modal.width // 6 + modal.left,
        bottom=modal.height // 4 + modal.top,
    )
    win_or_lose_image = cutout_image(source, target)

    mean_saturation: int = cv2.mean(cv2.cvtColor(win_or_lose_image, cv2.COLOR_BGR2HSV))[
        1
    ]
    # 'Win' has more vivid color than 'Lose'
    return mean_saturation > 50


def detect_opponent(
    reader: easyocr.Reader, grayscale: Image, modal: BoundingBox
) -> str | None:
    target = BoundingBox(
        left=modal.width * 5 // 6 + modal.left,
        top=modal.height // 7 + modal.top,
        right=modal.width + modal.left,
        bottom=modal.height // 5 + modal.top,
    )
    opponent_image: Image = cutout_image(grayscale, target)

    detected_chars: List[Character] = reader.readtext(opponent_image)  # type: ignore
    return join_chars(detected_chars) if len(detected_chars) > 0 else None
