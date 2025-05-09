import math

import cv2
import numpy
from cv2 import (
    LUT,  # type: ignore
    resize,
    warpAffine,
)

from taikoi2t.models.image import BoundingBox, Image, RelativeBox


def get_roi_bbox(source: BoundingBox, relative_roi: RelativeBox) -> BoundingBox:
    return BoundingBox(
        left=round(source.left + source.width * relative_roi.left),
        top=round(source.top + source.height * relative_roi.top),
        right=round(source.left + source.width * relative_roi.right),
        bottom=round(source.top + source.height * relative_roi.bottom),
    )


def resize_to(source: Image, width: int) -> Image:
    scale: float = width / source.shape[1]
    return resize(
        source, (width, int(source.shape[0] * scale)), interpolation=cv2.INTER_LANCZOS4
    )


def skew(source: Image, degree: float) -> Image:
    tan_theta: float = math.tan(math.radians(degree))
    mat = numpy.array([[1, tan_theta, 0], [0, 1, 0]], dtype=numpy.float64)
    height, width = source.shape[:2]
    return warpAffine(source, mat, (int(width + height * tan_theta), height))


def crop(image: Image, bbox: BoundingBox) -> Image:
    return image[bbox.top : bbox.bottom, bbox.left : bbox.right]


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


# for debug
def show_image(image: Image, title: str = "") -> None:
    cv2.imshow(title, image)
    cv2.waitKey()
    cv2.destroyAllWindows()
