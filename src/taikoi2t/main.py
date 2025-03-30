import math
import sys

import cv2
import numpy

# import easyocr  # type: ignore
from cv2 import (
    approxPolyDP,
    boundingRect,
    cvtColor,
    findContours,
    imread,
    threshold,
    warpAffine,
)
from numpy import float64, int32, uint8

type Image = numpy.typing.NDArray[uint8]
type Result = tuple[list[tuple[int32, int32]], str, float64]
type Bounding = tuple[int, int, int, int]

# reader = easyocr.Reader(["ja", "en"])

THRESHOLD: int = 120


def run() -> None:
    for path in sys.argv[1:]:
        source: Image = imread(path)
        if source is None:
            continue
        print(f"=== {path} ===")

        resultBounding = find_result_bounding(source)
        if resultBounding is None:
            continue

        studentsBounding = get_students_bounding(resultBounding)
        studentsImage = preprocess_students(source, studentsBounding)

        show_image(path, studentsImage)


def find_result_bounding(image: Image) -> Bounding | None:
    RESULT_RATIO: float = 0.43
    RATIO_EPS: float = 0.05

    imageWidth: int = image.shape[1]

    grayImage: Image = cvtColor(image, cv2.COLOR_BGR2GRAY)
    wbImage: Image = threshold(grayImage, 0, 255, cv2.THRESH_OTSU)[1]

    contours, _ = findContours(wbImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        bound: list[int] = boundingRect(approxPolyDP(contour, 3, True))
        if len(bound) < 4:
            continue

        [left, top, width, height] = bound
        ratio: float = height / width
        if width > imageWidth / 2 and abs(ratio - RESULT_RATIO) < RATIO_EPS:
            right: int = left + width
            bottom: int = top + height
            return (left, top, right, bottom)


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


def preprocess_students(source: Image, bounding: Bounding) -> Image:
    SKEW_ANGLE: float = math.tan(math.radians(14))
    SKEW_MAT = numpy.array([[1, SKEW_ANGLE, 0], [0, 1, 0]], dtype=float64)

    (left, top, right, bottom) = bounding
    width: int = right - left
    height: int = bottom - top

    footer: Image = cutout_image(source, bounding)
    return warpAffine(footer, SKEW_MAT, (int(width + height * SKEW_ANGLE), height))


def check() -> bool:
    return False


def load_image(path: str) -> bool:
    image = cv2.imread(path)
    print(type(image))
    print(image.shape)
    return image is not None


# def image_to_text(path: str) -> str:
#     results: list[Result] = reader.readtext(path)
#     for result in results:
#         print(result[1])
#     return ", ".join(r[1] for r in results)


def show_image(title: str, image: Image) -> None:
    cv2.imshow(title, image)
    cv2.waitKey()
    cv2.destroyAllWindows()
