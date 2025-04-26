import csv
import sys
from itertools import chain
from typing import List, Tuple

import cv2
import easyocr  # type: ignore
from cv2 import (
    approxPolyDP,  # type: ignore
    boundingRect,  # type: ignore
    cvtColor,
    findContours,
    imread,
    threshold,
)

from taikoi2t.args import VERBOSE_ERROR, VERBOSE_PRINT, Args, parse_args
from taikoi2t.bounding import size as bounding_size
from taikoi2t.image import (
    Bounding,
    Image,
    cutout_image,
    level_contrast,
    resize_to,
    skew,
)
from taikoi2t.ocr import Character, join_chars
from taikoi2t.student import (
    StudentDictionary,
    normalize_student_name,
    split_team,
)


def run() -> None:
    args = parse_args()

    with args.dictionary.open(mode="r", encoding="utf-8") as students_file:
        student_alias_pair: List[Tuple[str, str]] = [
            (row[0], row[1]) for row in csv.reader(students_file)
        ]
    if len(student_alias_pair) <= 0:
        print(
            f"FATAL: {args.dictionary.name} is invalid as student's dictionary",
            file=sys.stderr,
        )
        sys.exit(1)
    student_dictionary = StudentDictionary(student_alias_pair)

    reader = easyocr.Reader(["ja", "en"], verbose=args.verbose >= VERBOSE_PRINT)

    for path in args.files:
        if not path.exists():
            if args.verbose >= VERBOSE_ERROR:
                print(f"ERROR: {path} is not found", file=sys.stderr)
            else:
                print(empty_tsv_line(args))
            continue

        if args.verbose >= VERBOSE_PRINT:
            print(f"=== {path} ===")

        # imread returns None when error occurred
        source: Image | None = imread(path.as_posix())
        if source is None:  # type: ignore
            if args.verbose >= VERBOSE_ERROR:
                print(f"ERROR: {path} cannot read as an image", file=sys.stderr)
            else:
                print(empty_tsv_line(args))
            continue

        # for OCR
        grayscale: Image = cvtColor(source, cv2.COLOR_BGR2GRAY)

        result_bounding = find_result_bounding(grayscale)
        if result_bounding is None:
            if args.verbose >= VERBOSE_ERROR:
                print("ERROR: Cannot detect any result-box", file=sys.stderr)
            else:
                print(empty_tsv_line(args))
            continue

        detected_student_names = detect_student_names(
            reader, grayscale, result_bounding, student_dictionary.allow_char_list
        )

        # TODO: check 5 or less team
        if len(detected_student_names) < 12:
            if args.verbose >= VERBOSE_ERROR:
                print("ERROR: Student's names detection error", file=sys.stderr)
            else:
                print(empty_tsv_line(args))
            continue

        # matching student's names by Levenshtein distance
        matched_student_names: List[str] = [
            student_dictionary.match(detected) for detected in detected_student_names
        ]

        (player_st, player_sp) = split_team(matched_student_names[0:6])
        (opponent_st, opponent_sp) = split_team(matched_student_names[6:12])

        player_team = student_dictionary.apply_alias(
            chain(player_st, student_dictionary.sort_specials(player_sp))
        )
        opponent_team = student_dictionary.apply_alias(
            chain(opponent_st, student_dictionary.sort_specials(opponent_sp))
        )

        # passes colored source image because checking win or lose uses mean saturation of the area
        player_wins = check_player_wins(source, result_bounding)

        opponent = (
            detect_opponent(reader, grayscale, result_bounding) if args.opponent else ""
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
            print("\t".join(row))


def find_result_bounding(grayscale: Image) -> Bounding | None:
    RESULT_RATIO: float = 0.43
    RATIO_EPS: float = 0.05

    source_width: int = grayscale.shape[1]

    binary: Image = threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
    contours, _ = findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        rect: List[int] = boundingRect(approxPolyDP(contour, 3, True))
        if len(rect) < 4:
            continue

        [left, top, width, height] = rect
        ratio: float = height / width
        if width > source_width / 2 and abs(ratio - RESULT_RATIO) < RATIO_EPS:
            return (left, top, left + width, top + height)


def detect_student_names(
    reader: easyocr.Reader,
    grayscale: Image,
    result_bounding: Bounding,
    char_allow_list: str,
) -> List[str]:
    students_bounding = __get_students_bounding(result_bounding)
    student_name_images = __preprocess_students(grayscale, students_bounding)

    buffer: List[str] = list()
    for image in student_name_images:
        chars: List[Character] = reader.readtext(  # type: ignore
            image, paragraph=True, allowlist=char_allow_list
        )  # type: ignore
        name = normalize_student_name(join_chars(chars))
        buffer.append(name)
    return buffer


def __get_students_bounding(bounding: Bounding) -> Bounding:
    FOOTER_RATIO: float = 0.085
    (left, _, right, bottom) = bounding
    (_, height) = bounding_size(bounding)
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


def check_player_wins(source: Image, result_bounding: Bounding) -> bool:
    (left, top, _, _) = result_bounding
    (width, height) = bounding_size(result_bounding)

    bounding: Bounding = (
        width // 12 + left,
        height // 5 + top,
        width // 6 + left,
        height // 4 + top,
    )
    win_or_lose_image = cutout_image(source, bounding)

    mean_saturation: int = cv2.mean(cvtColor(win_or_lose_image, cv2.COLOR_BGR2HSV))[1]
    # 'Win' has more vivid color than 'Lose'
    return mean_saturation > 50


def detect_opponent(
    reader: easyocr.Reader, grayscale: Image, result_bounding: Bounding
) -> str:
    (left, top, _, _) = result_bounding
    (width, height) = bounding_size(result_bounding)

    bounding: Bounding = (
        width * 5 // 6 + left,
        height // 7 + top,
        width + left,
        height // 5 + top,
    )
    opponent_image: Image = cutout_image(grayscale, bounding)

    detected_chars: List[Character] = reader.readtext(opponent_image)  # type: ignore
    return join_chars(detected_chars)


def empty_tsv_line(settings: type[Args]) -> str:
    return "\t".join(['""'] * (14 if settings.opponent else 13))
