import csv
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

import cv2
import easyocr  # type: ignore

from taikoi2t.args import (
    VERBOSE_ERROR,
    VERBOSE_IMAGE,
    VERBOSE_PRINT,
    Args,
    parse_args,
    validate_args,
)
from taikoi2t.bounding import size as bounding_size
from taikoi2t.image import (
    Bounding,
    Image,
    cutout_image,
    level_contrast,
    resize_to,
    show_image,
    skew,
)
from taikoi2t.ocr import Character, join_chars
from taikoi2t.student import (
    StudentDictionary,
    normalize_student_name,
)


def run(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv or sys.argv)
    validate_args(args)

    student_alias_pair = read_student_alias_pair_file(args.dictionary)
    if student_alias_pair is None:
        print(
            f"FATAL: {args.dictionary.as_posix()} is invalid as student's dictionary",
            file=sys.stderr,
        )
        sys.exit(1)

    student_dictionary = StudentDictionary(student_alias_pair)

    if args.verbose >= VERBOSE_PRINT:
        print(student_dictionary.allow_char_list)

    reader = easyocr.Reader(["ja", "en"], verbose=args.verbose >= VERBOSE_PRINT)

    for path in args.files:
        if not path.exists():
            if args.verbose >= VERBOSE_ERROR:
                print(f"ERROR: {path.as_posix()} is not found", file=sys.stderr)
            print(error_line(args))
            continue

        if args.verbose >= VERBOSE_PRINT:
            print(f"=== {path.as_posix()} ===")

        # imread returns None when error occurred
        source: Image | None = cv2.imread(path.as_posix())
        if source is None:  # type: ignore
            if args.verbose >= VERBOSE_ERROR:
                print(
                    f"ERROR: {path.as_posix()} cannot read as an image", file=sys.stderr
                )
            print(error_line(args))
            continue

        # for OCR
        grayscale: Image = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)

        modal_bounding = find_modal_bounding(grayscale, args.verbose)
        if modal_bounding is None:
            if args.verbose >= VERBOSE_ERROR:
                print("ERROR: Cannot detect any result-box", file=sys.stderr)
            print(error_line(args))
            continue
        if args.verbose >= VERBOSE_IMAGE:
            (left, top, right, bottom) = modal_bounding
            show_image(
                cv2.rectangle(source.copy(), (left, top), (right, bottom), (0, 255, 0))
            )

        detected_student_names = detect_student_names(
            reader,
            grayscale,
            modal_bounding,
            student_dictionary.allow_char_list,
            args.verbose,
        )

        # TODO: check 5 or less team
        if len(detected_student_names) < 12:
            if args.verbose >= VERBOSE_ERROR:
                print("ERROR: Student's names detection error", file=sys.stderr)
            print(error_line(args))
            continue

        # matching student's names with the dictionary
        matched_student_names: List[str] = [
            student_dictionary.match(detected, args.verbose)
            for detected in detected_student_names
        ]

        player_team = student_dictionary.arrange_team(matched_student_names[0:6])
        opponent_team = student_dictionary.arrange_team(matched_student_names[6:12])

        # passes colored source image because checking win or lose uses mean saturation of the area
        player_wins = check_player_wins(source, modal_bounding)

        opponent: str = (
            detect_opponent(reader, grayscale, modal_bounding) if args.opponent else ""
        )

        row: List[str] = (
            ["TRUE" if player_wins else "FALSE"]
            + player_team
            + ([opponent] if args.opponent else [])
            + opponent_team
        )
        if args.verbose >= VERBOSE_PRINT:
            print(row)
        else:
            print(("," if args.csv else "\t").join(row))


def read_student_alias_pair_file(path: Path) -> List[Tuple[str, str]] | None:
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


def find_modal_bounding(grayscale: Image, verbose: int = 0) -> Bounding | None:
    RESULT_ASPECT_RATIO: float = 2.33
    ASPECT_RATIO_EPS: float = 0.05
    APPROX_PRECISION: float = 0.03

    source_width: int = grayscale.shape[1]

    binary: Image = cv2.threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    preview: Image | None = None
    if verbose >= VERBOSE_IMAGE:
        preview = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    result: Bounding | None = None
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
            result = (left, top, left + width, top + height)

    if preview is not None:
        show_image(preview)

    return result


def detect_student_names(
    reader: easyocr.Reader,
    grayscale: Image,
    modal: Bounding,
    char_allow_list: str,
    verbose: int = 0,
) -> List[str]:
    students_bounding = __get_students_bounding(modal)
    student_name_images = __preprocess_students(grayscale, students_bounding)

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


def __get_students_bounding(modal: Bounding) -> Bounding:
    FOOTER_RATIO: float = 0.085
    (left, _, right, bottom) = modal
    (_, height) = bounding_size(modal)
    footer_height = int(FOOTER_RATIO * height)
    footer_top = int(bottom - footer_height)
    return (left, footer_top, right, bottom)


def __preprocess_students(grayscale: Image, bounding: Bounding) -> List[Image]:
    WIDTH: int = 4000

    footer = cutout_image(grayscale, bounding)
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
        results.append(cutout_image(leveled, (x, 0, (x + PITCH), height)))
    for x in range(OPPONENT_TEAM_LEFT, OPPONENT_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(cutout_image(leveled, (x, 0, (x + PITCH), height)))

    return results


def check_player_wins(source: Image, modal: Bounding) -> bool:
    (left, top, _, _) = modal
    (width, height) = bounding_size(modal)

    bounding: Bounding = (
        width // 12 + left,
        height // 5 + top,
        width // 6 + left,
        height // 4 + top,
    )
    win_or_lose_image = cutout_image(source, bounding)

    mean_saturation: int = cv2.mean(cv2.cvtColor(win_or_lose_image, cv2.COLOR_BGR2HSV))[
        1
    ]
    # 'Win' has more vivid color than 'Lose'
    return mean_saturation > 50


def detect_opponent(reader: easyocr.Reader, grayscale: Image, modal: Bounding) -> str:
    (left, top, _, _) = modal
    (width, height) = bounding_size(modal)

    bounding: Bounding = (
        width * 5 // 6 + left,
        height // 7 + top,
        width + left,
        height // 5 + top,
    )
    opponent_image: Image = cutout_image(grayscale, bounding)

    detected_chars: List[Character] = reader.readtext(opponent_image)  # type: ignore
    return join_chars(detected_chars)


def error_line(settings: Args) -> str:
    return ("," if settings.csv else "\t").join(
        ["FALSE"] + (["Error"] * (13 if settings.opponent else 12))
    )
