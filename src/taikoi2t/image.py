import math

import cv2
import numpy
from cv2 import (
    LUT,  # type: ignore
    resize,
    warpAffine,
)

from taikoi2t.types import Bounding

type Image = numpy.typing.NDArray[numpy.uint8]


def resize_to(source: Image, width: int) -> Image:
    scale: float = width / source.shape[1]
    return resize(
        source, (width, int(source.shape[0] * scale)), interpolation=cv2.INTER_LANCZOS4
    )


def skew(source: Image, degree: float) -> Image:
    tanTheta: float = math.tan(math.radians(degree))
    mat = numpy.array([[1, tanTheta, 0], [0, 1, 0]], dtype=numpy.float64)
    height, width = source.shape[:2]
    return warpAffine(source, mat, (int(width + height * tanTheta), height))


def cutout_image(image: Image, bounding: Bounding) -> Image:
    (left, top, right, bottom) = bounding
    return image[top:bottom, left:right]


#      ___
#     /|
#    / |
# __/  |
#  x0  x1
def level_contrast(image: Image, x0: int, x1: int) -> Image:
    x0 = max(x0, 0)
    x1 = min(x1, 255)
    gain: float = 255.0 / (x1 - x0)
    bias: float = -x0 * gain
    x = numpy.arange(256, dtype=numpy.uint8)
    y = numpy.clip(x * gain + bias, 0, 255)
    return LUT(image, y).astype(numpy.uint8)


def show_image(title: str, image: Image) -> None:
    cv2.imshow(title, image)
    cv2.waitKey()
    cv2.destroyAllWindows()
