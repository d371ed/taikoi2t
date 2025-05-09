from typing import Sequence

import cv2

from taikoi2t.implements.image import show_image
from taikoi2t.models.args import VERBOSE_IMAGE
from taikoi2t.models.image import BoundingBox, Image


def find_modal(grayscale: Image, verbose: int = 0) -> BoundingBox | None:
    RESULT_ASPECT_RATIO: float = 2.33
    ASPECT_RATIO_EPS: float = 0.05
    APPROX_PRECISION: float = 0.03

    source_width: int = grayscale.shape[1]

    binary: Image = cv2.threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    preview: Image | None = None
    if verbose >= VERBOSE_IMAGE:
        preview = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    result: BoundingBox | None = None
    for contour in contours:
        epsilon: float = APPROX_PRECISION * cv2.arcLength(contour, True)  # type: ignore
        approx = cv2.approxPolyDP(contour, epsilon, True)  # type: ignore
        rect: Sequence[int] = cv2.boundingRect(approx)  # type: ignore

        [left, top, width, height] = rect
        if preview is not None:
            cv2.drawContours(preview, [approx], -1, (0, 0, 255))

        aspect_ratio: float = width / height
        if (
            width > source_width / 2
            and abs(aspect_ratio - RESULT_ASPECT_RATIO) < ASPECT_RATIO_EPS
        ):
            result = BoundingBox(left, top, left + width, top + height)

    if preview is not None:
        show_image(preview)

    return result
