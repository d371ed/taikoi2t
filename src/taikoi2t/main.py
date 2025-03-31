import csv
import sys

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

from taikoi2t.image import Image, cutout_image, level_contrast, resize_to, skew
from taikoi2t.ocr import Character
from taikoi2t.types import Bounding

reader = easyocr.Reader(["ja", "en"])


def run() -> None:
    with open("./students.csv", "r", encoding="utf-8") as studentsFile:
        studentDictionary: list[tuple[str, str]] = [
            (row[0], row[1]) for row in csv.reader(studentsFile)
        ]

    studentCharAllowList: str = (
        "".join(set("".join(s[0] for s in studentDictionary))) + "()"
    )
    print(studentCharAllowList)

    for path in sys.argv[1:]:
        source: Image = imread(path)
        if source is None:
            continue
        print(f"=== {path} ===")

        grayscale: Image = cvtColor(source, cv2.COLOR_BGR2GRAY)

        resultBounding = find_result_bounding(grayscale)
        if resultBounding is None:
            continue

        studentsBounding = get_students_bounding(resultBounding)
        studentNameImages = preprocess_students(grayscale, studentsBounding)

        detectedNames: list[str] = list()
        for studentNameImage in studentNameImages:
            chars: list[Character] = reader.readtext(  # type: ignore
                studentNameImage, paragraph=True, allowlist=studentCharAllowList
            )  # type: ignore
            detectedNames.append("".join(c[1] for c in chars).replace(" ", ""))

        print(detectedNames)


def find_result_bounding(grayscale: Image) -> Bounding | None:
    RESULT_RATIO: float = 0.43
    RATIO_EPS: float = 0.05

    sourceWidth: int = grayscale.shape[1]

    binary: Image = threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
    contours, _ = findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        bounding: list[int] = boundingRect(approxPolyDP(contour, 3, True))
        if len(bounding) < 4:
            continue

        [left, top, width, height] = bounding
        ratio: float = height / width
        if width > sourceWidth / 2 and abs(ratio - RESULT_RATIO) < RATIO_EPS:
            return (left, top, left + width, top + height)


def get_students_bounding(bounding: Bounding) -> Bounding:
    FOOTER_RATIO: float = 0.085
    (left, top, right, bottom) = bounding
    height: int = bottom - top
    footerHeight = int(FOOTER_RATIO * height)
    footerTop = int(bottom - footerHeight)
    return (left, footerTop, right, bottom)


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
