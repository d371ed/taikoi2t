import logging
import math
from pathlib import Path
from typing import Iterable, Tuple

import cv2
import numpy

from taikoi2t.models.image import BoundingBox, Image, ImageMeta, RelativeBox

logger: logging.Logger = logging.getLogger("taikoi2t.image")


def sanitize_roi(roi: BoundingBox, image_width: int, image_height: int) -> BoundingBox:
    left, right = (
        (roi.left, roi.right) if roi.left <= roi.right else (roi.right, roi.left)
    )
    top, bottom = (
        (roi.top, roi.bottom) if roi.top <= roi.bottom else (roi.bottom, roi.top)
    )
    return BoundingBox(
        left=__clamp(left, 0, image_width),
        top=__clamp(top, 0, image_height),
        right=__clamp(right, 0, image_width),
        bottom=__clamp(bottom, 0, image_height),
    )


def get_roi_bbox(source: BoundingBox, relative_roi: RelativeBox) -> BoundingBox:
    return BoundingBox(
        left=round(source.left + source.width * relative_roi.left),
        top=round(source.top + source.height * relative_roi.top),
        right=round(source.left + source.width * relative_roi.right),
        bottom=round(source.top + source.height * relative_roi.bottom),
    )


def read_image(path: Path) -> Image | None:
    try:
        # imread returns None when error occurred...?
        return cv2.imread(path.as_posix())
    except Exception as e:  # unexpected error
        logger.error(e)
        return None


def convert_to_grayscale(source: Image) -> Image | None:
    try:
        return cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        logger.error(e)
        return None


def resize_to(source: Image, width: int) -> Image | None:
    try:
        scale: float = width / source.shape[1]
        return cv2.resize(
            source,
            (width, int(source.shape[0] * scale)),
            interpolation=cv2.INTER_LANCZOS4,
        )
    except Exception as e:
        logger.error(e)
        return None


def skew(source: Image, degree: float) -> Image | None:
    tan_theta: float = math.tan(math.radians(degree))
    try:
        mat = numpy.array([[1, tan_theta, 0], [0, 1, 0]], dtype=numpy.float64)
        height, width = source.shape[:2]
        return cv2.warpAffine(source, mat, (int(width + height * tan_theta), height))
    except Exception as e:
        logger.error(e)
        return None


def smooth(source: Image, kernel_size: int) -> Image | None:
    try:
        return cv2.GaussianBlur(source, (kernel_size, kernel_size), 0)
    except Exception as e:
        logger.error(e)
        return None


def sharpen(source: Image, k: float) -> Image | None:
    try:
        laplacian: Image = cv2.Laplacian(source, cv2.CV_64F)  # type: ignore
        return cv2.convertScaleAbs(source - k * laplacian)  # type: ignore
    except Exception as e:
        logger.error(e)
        return None


def crop(image: Image, bbox: BoundingBox) -> Image:
    height, width = image.shape[:2]
    sanitized = sanitize_roi(bbox, image_width=width, image_height=height)
    return image[sanitized.top : sanitized.bottom, sanitized.left : sanitized.right]


#      ___
#     /|
#    / |
# __/  |
#  x0  x1
def level_contrast(image: Image, x0: int, x1: int) -> Image | None:
    x0 = max(x0, 0)
    x1 = min(x1, 255)
    gain: float = 255.0 / (x1 - x0)
    bias: float = -x0 * gain
    try:
        x = numpy.arange(256, dtype=numpy.uint8)
        y = numpy.clip(x * gain + bias, 0, 255)
        return cv2.LUT(image, y).astype(numpy.uint8)  # type: ignore
    except Exception as e:
        logger.error(e)
        return None


def binarize(image: Image) -> Image | None:
    try:
        return cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)[1]
    except Exception as e:
        logger.error(e)
        return None


# for debug
def show_image(image: Image, title: str = "") -> None:
    try:
        cv2.imshow(title, image)
        cv2.waitKey()
        cv2.destroyAllWindows()
    except Exception as e:
        logger.error(e)


# for debug
def show_bboxes(
    image: Image, bboxes: Iterable[BoundingBox], to_bgr: bool = False
) -> None:
    try:
        preview: Image = (
            cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if to_bgr else image.copy()
        )
        for bbox in bboxes:
            if bbox.is_empty():
                continue
            cv2.rectangle(
                preview, (bbox.left, bbox.top), (bbox.right, bbox.bottom), (0, 255, 0)
            )
        show_image(preview)
    except Exception as e:
        logger.error(e)


def new_image_meta(
    path: Path,
    image_dimension: Tuple[int, int] | None = None,
    modal: BoundingBox | None = None,
) -> ImageMeta:
    stat = path.stat() if path.exists() else None
    btime, mtime = (
        (None, None) if stat is None else (stat.st_birthtime_ns, stat.st_mtime_ns)
    )
    width, height = (None, None) if image_dimension is None else image_dimension
    return ImageMeta(
        path=path.as_posix(),
        name=path.name,
        birth_time_ns=btime,
        modify_time_ns=mtime,
        width=width,
        height=height,
        modal=modal,
    )


def __clamp(value: int, lower_limit: int, higher_limit: int) -> int:
    return min(max(value, lower_limit), higher_limit)
