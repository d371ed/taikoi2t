import csv
import sys
from typing import cast

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

from taikoi2t.image import (
    Image,
    cutout_image,
    level_contrast,
    resize_to,
    skew,
)
from taikoi2t.ocr import Character
from taikoi2t.types import Bounding, Specials, Strikers

reader = easyocr.Reader(["ja", "en"])


def run() -> None:
    with open("./students.csv", "r", encoding="utf-8") as students_file:
        student_dictionary: list[tuple[str, str]] = [
            (normalize_student_name(row[0]), row[1])
            for row in csv.reader(students_file)
        ]

    char_allow_list: str = (
        "".join(set("".join(s[0] for s in student_dictionary))) + "()"
    )
    # print(char_allow_list)

    ordered_students: list[str] = [pair[0] for pair in student_dictionary]
    # print(ordered_students)

    student_mapping: dict[str, str] = dict(student_dictionary)
    # print(student_mapping)

    for path in sys.argv[1:]:
        source: Image = imread(path)
        print(f"=== {path} ===")

        grayscale: Image = cvtColor(source, cv2.COLOR_BGR2GRAY)

        result_bounding = find_result_bounding(grayscale)
        if result_bounding is None:
            continue

        students_bounding = get_students_bounding(result_bounding)
        student_name_images = preprocess_students(grayscale, students_bounding)

        detected_student_names: list[str] = list()
        for student_name_image in student_name_images:
            chars: list[Character] = reader.readtext(  # type: ignore
                student_name_image, paragraph=True, allowlist=char_allow_list
            )  # type: ignore
            detected_student_names.append(
                normalize_student_name("".join(c[1] for c in chars).replace(" ", ""))
            )

        # print(detected_student_names)

        matched_student_names: list[str] = [
            process.extractOne(detected, ordered_students)[0]
            for detected in detected_student_names
        ]
        # print(matched_student_names)

        if len(matched_student_names) != 12:
            continue

        left_team_strikers: Strikers = cast(Strikers, matched_student_names[0:4])
        left_team_specials: Specials = cast(Specials, matched_student_names[4:6])

        right_team_strikers: Strikers = cast(Strikers, matched_student_names[6:10])
        right_team_specials: Specials = cast(Specials, matched_student_names[10:12])

        if ordered_students.index(left_team_specials[0]) > ordered_students.index(
            left_team_specials[1]
        ):
            left_team_specials = cast(Specials, tuple(reversed(left_team_specials)))
        if ordered_students.index(right_team_specials[0]) > ordered_students.index(
            right_team_specials[1]
        ):
            right_team_specials = cast(Specials, tuple(reversed(right_team_specials)))

        # print(
        #     (
        #         (left_team_strikers, left_team_specials),
        #         (right_team_strikers, right_team_specials),
        #     )
        # )

        mapped_left_team: list[str] = list(
            (name if student_mapping[name] == "" else student_mapping[name])
            for name in (left_team_strikers + left_team_specials)
        )
        print(mapped_left_team)

        mapped_right_team: list[str] = list(
            (name if student_mapping[name] == "" else student_mapping[name])
            for name in (right_team_strikers + right_team_specials)
        )
        print(mapped_right_team)

        result_width: int = result_bounding[2] - result_bounding[0]
        result_height: int = result_bounding[3] - result_bounding[1]
        left_result_bounding: Bounding = (
            result_width // 12 + result_bounding[0],
            result_height // 5 + result_bounding[1],
            result_width // 6 + result_bounding[0],
            result_height // 4 + result_bounding[1],
        )
        left_result_image: Image = cutout_image(
            cvtColor(source, cv2.COLOR_BGR2HSV), left_result_bounding
        )
        saturation: int = cv2.mean(left_result_image)[1]
        left_wins: bool = saturation > 50
        print("win" if left_wins else "lose")


def find_result_bounding(grayscale: Image) -> Bounding | None:
    RESULT_RATIO: float = 0.43
    RATIO_EPS: float = 0.05

    source_width: int = grayscale.shape[1]

    binary: Image = threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
    contours, _ = findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        bounding: list[int] = boundingRect(approxPolyDP(contour, 3, True))
        if len(bounding) < 4:
            continue

        [left, top, width, height] = bounding
        ratio: float = height / width
        if width > source_width / 2 and abs(ratio - RESULT_RATIO) < RATIO_EPS:
            return (left, top, left + width, top + height)


def get_students_bounding(bounding: Bounding) -> Bounding:
    FOOTER_RATIO: float = 0.085
    (left, top, right, bottom) = bounding
    height: int = bottom - top
    footer_height = int(FOOTER_RATIO * height)
    footer_top = int(bottom - footer_height)
    return (left, footer_top, right, bottom)


def preprocess_students(grayscale: Image, bounding: Bounding) -> list[Image]:
    WIDTH: int = 4000
    PITCH_RATIO: float = 113 / 1844
    PITCH: int = int(WIDTH * PITCH_RATIO)
    TEAM_WIDTH: int = PITCH * 6

    footer: Image = cutout_image(grayscale, bounding)
    resized: Image = resize_to(footer, WIDTH)
    skewed: Image = skew(resized, 14.0)
    leveled: Image = level_contrast(skewed, 112, 192)

    height: int = leveled.shape[1]
    results: list[Image] = list()
    L_TEAM_LEFT: int = 216
    for x in range(L_TEAM_LEFT, L_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(leveled[0:height, x : (x + PITCH)])
    R_TEAM_LEFT: int = WIDTH // 2 + 292
    for x in range(R_TEAM_LEFT, R_TEAM_LEFT + TEAM_WIDTH, PITCH):
        results.append(leveled[0:height, x : (x + PITCH)])

    return results


def normalize_student_name(name: str) -> str:
    return name.replace("(", "（").replace(")", "）")
