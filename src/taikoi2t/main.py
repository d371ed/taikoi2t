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

from taikoi2t.image import Image, cutout_image, level_contrast, resize_to, skew
from taikoi2t.ocr import Character
from taikoi2t.types import Bounding, Specials, Strikers

reader = easyocr.Reader(["ja", "en"])


def run() -> None:
    with open("./students.csv", "r", encoding="utf-8") as studentsFile:
        studentDictionary: list[tuple[str, str]] = [
            (normalizeStudentName(row[0]), row[1]) for row in csv.reader(studentsFile)
        ]

    studentCharAllowList: str = (
        "".join(set("".join(s[0] for s in studentDictionary))) + "()"
    )
    print(studentCharAllowList)

    studentKeys: list[str] = [pair[0] for pair in studentDictionary]
    print(studentKeys)

    studentMapping: dict[str, str] = dict(studentDictionary)
    print(studentMapping)

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
            detectedNames.append(
                normalizeStudentName("".join(c[1] for c in chars).replace(" ", ""))
            )

        print(detectedNames)

        matchedNames: list[str] = [
            process.extractOne(detected, studentKeys)[0] for detected in detectedNames
        ]
        print(matchedNames)

        if len(matchedNames) != 12:
            continue

        leftTeamStrikers: Strikers = cast(Strikers, matchedNames[0:4])
        leftTeamSpecials: Specials = cast(Specials, matchedNames[4:6])

        rightTeamStrikers: Strikers = cast(Strikers, matchedNames[6:10])
        rightTeamSpecials: Specials = cast(Specials, matchedNames[10:12])

        if studentKeys.index(leftTeamSpecials[0]) > studentKeys.index(
            leftTeamSpecials[1]
        ):
            leftTeamSpecials = cast(Specials, tuple(reversed(leftTeamSpecials)))
        if studentKeys.index(rightTeamSpecials[0]) > studentKeys.index(
            rightTeamSpecials[1]
        ):
            rightTeamSpecials = cast(Specials, tuple(reversed(rightTeamSpecials)))

        print(
            (
                (leftTeamStrikers, leftTeamSpecials),
                (rightTeamStrikers, rightTeamSpecials),
            )
        )

        mappedLeftTeam: list[str] = list(
            (name if studentMapping[name] == "" else studentMapping[name])
            for name in (leftTeamStrikers + leftTeamSpecials)
        )
        print(mappedLeftTeam)

        mappedRightTeam: list[str] = list(
            (name if studentMapping[name] == "" else studentMapping[name])
            for name in (rightTeamStrikers + rightTeamSpecials)
        )
        print(mappedRightTeam)


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


def normalizeStudentName(name: str) -> str:
    return name.replace("(", "（").replace(")", "）")
