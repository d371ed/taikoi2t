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

# reader = easyocr.Reader(["ja", "en"])

THRESHOLD: int = 120


def run() -> None:
    for path in sys.argv[1:]:
        image: Image = imread(path)
        if image is None:
            continue
        print(f"=== {path} ===")

        bounding = get_result_bounding(image)
        if bounding is not None:
            (left, top, right, bottom) = bounding
            width: int = right - left
            height: int = bottom - top
            footerHeight: int = int(0.085 * height)
            footerTop: int = int(bottom - footerHeight)
            footer: Image = image[footerTop:bottom, left:right]

            angle: float = math.tan(math.radians(14))
            mat = numpy.array([[1, angle, 0], [0, 1, 0]], dtype=float64)
            skewed: Image = warpAffine(
                footer, mat, (int(width + footerHeight * angle), footerHeight)
            )

            cv2.imshow(path, skewed)
            cv2.waitKey()
            cv2.destroyAllWindows()


def get_result_bounding(image: Image) -> tuple[int, int, int, int] | None:
    RESULT_RATIO: float = 0.43

    imageWidth: int = image.shape[1]
    imageHeight: int = image.shape[0]
    print(f"width: {imageWidth}, height: {imageHeight}")

    grayImage: Image = cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret: int
    wbImage: Image
    ret, wbImage = threshold(grayImage, 0, 255, cv2.THRESH_OTSU)
    print(f"threshold: {ret}")

    contours, _ = findContours(wbImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        bound: list[int] = boundingRect(approxPolyDP(contour, 3, True))
        if len(bound) < 4:
            continue

        [left, top, width, height] = bound
        ratio: float = height / width
        if width > imageWidth / 2 and abs(ratio - RESULT_RATIO) < 0.01:
            right: int = left + width
            bottom: int = top + height
            # rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

            print(f"bound width: {width}, height: {height}")
            print(f"ratio: {ratio}")

            return (left, top, right, bottom)


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
