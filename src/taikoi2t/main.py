import math
import sys

import cv2
import easyocr  # type: ignore
import numpy
from cv2 import (
    LUT,
    approxPolyDP,
    boundingRect,
    cvtColor,
    findContours,
    imread,
    rectangle,
    resize,
    threshold,
    warpAffine,
)
from numpy import float64, uint8

type Image = numpy.typing.NDArray[uint8]
type Character = tuple[list[tuple[int, int]], str, float]
type Bounding = tuple[int, int, int, int]

STUDENTS_PITCH = int(1844 // 113)

reader = easyocr.Reader(["ja", "en"])


def run() -> None:
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
        leftTeamImage, rightTeamImage = preprocess_students(grayscale, studentsBounding)

        leftTeamChars: list[Character] = reader.readtext(leftTeamImage)  # type: ignore
        rightTeamChars: list[Character] = reader.readtext(rightTeamImage)  # type: ignore

        pitch: int = int(
            (leftTeamImage.shape[1] + rightTeamImage.shape[1]) / 1844.0 * 113
        )
        print(f"pitch: {pitch}")

        for char in leftTeamChars:
            print(char)
            rectangle(leftTeamImage, char[0][0], char[0][2], 0, 1)
        print(groupCharacters(leftTeamChars, pitch))
        show_image(path, leftTeamImage)

        for char in rightTeamChars:
            print(char)
            rectangle(rightTeamImage, char[0][0], char[0][2], 0, 1)
        print(groupCharacters(rightTeamChars, pitch))
        show_image(path, rightTeamImage)

        print(", ".join(r[1] for r in (leftTeamChars + rightTeamChars)))


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


def cutout_image(image: Image, bounding: Bounding) -> Image:
    (left, top, right, bottom) = bounding
    return image[top:bottom, left:right]


def preprocess_students(grayscale: Image, bounding: Bounding) -> tuple[Image, Image]:
    footer: Image = cutout_image(grayscale, bounding)
    WIDTH: int = 4000
    resized: Image = resize_to(footer, WIDTH)
    skewed: Image = skew(resized, 14.0)

    P0 = 112
    P1 = 192
    GAIN: float = 256.0 / (P1 - P0)
    BIAS: float = -P0 * GAIN
    x = numpy.arange(256, dtype=numpy.uint8)
    y = numpy.clip(x * GAIN + BIAS, 0, 255)
    leveled: Image = LUT(skewed, y).astype(numpy.uint8)

    height: int = leveled.shape[1]
    center: int = WIDTH // 2
    MARGIN: int = 100

    return (
        leveled[0:height, MARGIN:center],
        leveled[0:height, center : (WIDTH - MARGIN)],
    )


def groupCharacters(chars: list[Character], pitch: int) -> list[str]:
    leftmost: int = 9999999
    rightmost: int = 0
    for char in chars:
        leftmost = min(leftmost, char[0][0][0])
        rightmost = max(rightmost, char[0][2][0])
    students: list[str] = list()
    margin: int = pitch // 10
    for groupX in range(leftmost, rightmost, pitch):
        buffer: str = ""
        for char in chars:
            x: int = char[0][0][0]
            if x >= groupX - margin and x < groupX + pitch - margin:
                buffer += char[1]
        if len(buffer) > 0:
            students.append(buffer)
    return students


def skew(source: Image, degree: float) -> Image:
    tanTheta: float = math.tan(math.radians(degree))
    mat = numpy.array([[1, tanTheta, 0], [0, 1, 0]], dtype=float64)
    height, width = source.shape[:2]
    return warpAffine(source, mat, (int(width + height * tanTheta), height))


def resize_to(source: Image, width: int) -> Image:
    scale: float = width / source.shape[1]
    return resize(
        source, (width, int(source.shape[0] * scale)), interpolation=cv2.INTER_LANCZOS4
    )


def check() -> bool:
    return False


def load_image(path: str) -> bool:
    image = cv2.imread(path)
    print(type(image))
    print(image.shape)
    return image is not None


def image_to_text(path: str) -> str:
    results: list[Character] = reader.readtext(path)
    for result in results:
        print(result[1])
    return ", ".join(r[1] for r in results)


def show_image(title: str, image: Image) -> None:
    cv2.imshow(title, image)
    cv2.waitKey()
    cv2.destroyAllWindows()
