import csv
from itertools import chain
from typing import Dict, Iterable, List, Sequence, Tuple

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

from taikoi2t import utils
from taikoi2t.args import parse_args
from taikoi2t.image import (
    Image,
    cutout_image,
    level_contrast,
    resize_to,
    skew,
)
from taikoi2t.ocr import Character, join_chars
from taikoi2t.types import Bounding, Specials, Strikers


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
        source: Image = imread(path.as_posix())
        if args.verbose:
            print(f"=== {path} ===")

        grayscale: Image = cvtColor(source, cv2.COLOR_BGR2GRAY)

        result_bounding = find_result_bounding(grayscale)
        if result_bounding is None:
            continue

        students_bounding = get_students_bounding(result_bounding)
        student_name_images = preprocess_students(grayscale, students_bounding)

        detected_student_names: List[str] = list()
        for image in student_name_images:
            chars: List[Character] = reader.readtext(  # type: ignore
                image, paragraph=True, allowlist=char_allow_list
            )  # type: ignore
            name = normalize_student_name(join_chars(chars))
            detected_student_names.append(name)

        matched_student_names: List[str] = [
            process.extractOne(detected, ordered_students)[0] if detected != "" else ""
            for detected in detected_student_names
        ]

        if len(matched_student_names) < 12:
            continue
        (left_st, left_sp) = split_team(matched_student_names[0:6])
        (right_st, right_sp) = split_team(matched_student_names[6:12])

        mapped_left_team = apply_alias(
            chain(left_st, sort_specials(left_sp, ordered_students)), student_mapping
        )
        mapped_right_team = apply_alias(
            chain(right_st, sort_specials(right_sp, ordered_students)), student_mapping
        )

        left_wins = check_left_team_wins(source, result_bounding)
        opponent = detect_opponent(reader, grayscale, result_bounding)

        row: List[str] = (
            ["TRUE" if left_wins else "FALSE"]
            + mapped_left_team
            + [opponent]
            + mapped_right_team
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
        bounding: List[int] = boundingRect(approxPolyDP(contour, 3, True))
        if len(bounding) < 4:
            continue

        [left, top, width, height] = bounding
        ratio: float = height / width
        if width > source_width / 2 and abs(ratio - RESULT_RATIO) < RATIO_EPS:
            return (left, top, left + width, top + height)


def get_students_bounding(bounding: Bounding) -> Bounding:
    FOOTER_RATIO: float = 0.085
    (left, _, right, bottom) = bounding
    (_, height) = utils.size(bounding)
    footer_height = int(FOOTER_RATIO * height)
    footer_top = int(bottom - footer_height)
    return (left, footer_top, right, bottom)


def preprocess_students(grayscale: Image, bounding: Bounding) -> List[Image]:
    WIDTH: int = 4000
    PITCH_RATIO: float = 113 / 1844
    PITCH: int = int(WIDTH * PITCH_RATIO)
    TEAM_WIDTH: int = PITCH * 6

    footer: Image = cutout_image(grayscale, bounding)
    resized: Image = resize_to(footer, WIDTH)
    skewed: Image = skew(resized, 14.0)
    leveled: Image = level_contrast(skewed, 112, 192)

    height: int = leveled.shape[1]
    results: List[Image] = list()
    L_TEAM_LEFT: int = 216
    for x in range(L_TEAM_LEFT, L_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(leveled[0:height, x : (x + PITCH)])
    R_TEAM_LEFT: int = WIDTH // 2 + 292
    for x in range(R_TEAM_LEFT, R_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(leveled[0:height, x : (x + PITCH)])

    return results


def check_left_team_wins(source: Image, result_bounding: Bounding) -> bool:
    (left, top, _, _) = result_bounding
    (width, height) = utils.size(result_bounding)

    bounding: Bounding = (
        width // 12 + left,
        height // 5 + top,
        width // 6 + left,
        height // 4 + top,
    )
    win_or_lose_image: Image = cutout_image(source, bounding)

    mean_saturation: int = cv2.mean(cvtColor(win_or_lose_image, cv2.COLOR_BGR2HSV))[1]
    # 'Win' has more vivid color than 'Lose'
    return mean_saturation > 50


def detect_opponent(
    reader: easyocr.Reader, grayscale: Image, result_bounding: Bounding
) -> str:
    (left, top, _, _) = result_bounding
    (width, height) = utils.size(result_bounding)

    bounding: Bounding = (
        width * 5 // 6 + left,
        height // 7 + top,
        width + left,
        height // 5 + top,
    )
    opponent_image: Image = cutout_image(grayscale, bounding)

    detected_chars: List[Character] = reader.readtext(opponent_image)  # type: ignore
    return join_chars(detected_chars)


def split_team(students: Sequence[str]) -> Tuple[Strikers, Specials]:
    ss: Sequence[str] = (
        list(chain(students, [""] * (6 - len(students))))
        if len(students) < 6
        else students
    )
    return (
        (ss[0], ss[1], ss[2], ss[3]),
        (ss[4], ss[5]),
    )


def sort_specials(specials: Specials, ordered_students: Sequence[str]) -> Specials:
    return (
        (specials[1], specials[0])
        if ordered_students.index(specials[0]) > ordered_students.index(specials[1])
        else (specials[0], specials[1])
    )


def apply_alias(names: Iterable[str], mapping: Dict[str, str]) -> List[str]:
    return [(name if mapping[name] == "" else mapping[name]) for name in names]


def normalize_student_name(name: str) -> str:
    return name.replace("(", "（").replace(")", "）")
