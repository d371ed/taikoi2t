import csv
import sys
from itertools import chain
from typing import Dict, List, Tuple

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
from rapidfuzz import process

from taikoi2t.args import parse_args
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
    apply_alias,
    normalize_student_name,
    sort_specials,
    split_team,
)


def run() -> None:
    args = parse_args()

    with args.dictionary.open(mode="r", encoding="utf-8") as students_file:
        student_dictionary: List[Tuple[str, str]] = [
            (normalize_student_name(row[0]), row[1])
            for row in csv.reader(students_file)
        ]

    char_allow_list: str = (
        "".join(set("".join(s[0] for s in student_dictionary))) + "()"
    )
    ordered_students: List[str] = [pair[0] for pair in student_dictionary]
    student_mapping: Dict[str, str] = dict(student_dictionary)

    reader = easyocr.Reader(["ja", "en"], verbose=args.verbose)

    for path in args.files:
        if not path.exists():
            if args.verbose:
                print(f"ERROR: {path} not found", sys.stderr)
            else:
                print(empty_csv_line(args.opponent))
            continue

        source: Image = imread(path.as_posix())  # TODO: error handling
        if args.verbose:
            print(f"=== {path} ===")

        # for OCR
        grayscale: Image = cvtColor(source, cv2.COLOR_BGR2GRAY)

        result_bounding = find_result_bounding(grayscale)
        if result_bounding is None:
            if args.verbose:
                print("ERROR: Cannot detect any result-box", sys.stderr)
            else:
                print(empty_csv_line(args.opponent))
            continue

        detected_student_names = detect_student_names(
            reader, grayscale, result_bounding, char_allow_list
        )

        # TODO: check 5 or less team
        if len(detected_student_names) < 12:
            if args.verbose:
                print("ERROR: Student's names detection error", sys.stderr)
            else:
                print(empty_csv_line(args.opponent))
            continue

        # matching student's names by Levenshtein distance
        matched_student_names: List[str] = [
            process.extractOne(detected, ordered_students)[0] if detected != "" else ""
            for detected in detected_student_names
        ]

        (player_st, player_sp) = split_team(matched_student_names[0:6])
        (opponent_st, opponent_sp) = split_team(matched_student_names[6:12])

        player_team = apply_alias(
            chain(player_st, sort_specials(player_sp, ordered_students)),
            student_mapping,
        )
        opponent_team = apply_alias(
            chain(opponent_st, sort_specials(opponent_sp, ordered_students)),
            student_mapping,
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
        if args.verbose:
            print(row)
        else:
            print(",".join(row))


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


def empty_csv_line(opponent: bool) -> str:
    return ",".join([""] * (14 if opponent else 13))
