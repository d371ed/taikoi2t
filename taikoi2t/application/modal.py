import logging
from typing import Sequence

import cv2

from taikoi2t.implements.image import sanitize_roi, show_image
from taikoi2t.models.args import VERBOSE_IMAGE
from taikoi2t.models.image import BoundingBox, Image

logger: logging.Logger = logging.getLogger("taikoi2t.modal")

RESULT_ASPECT_RATIO: float = 2.33
ASPECT_RATIO_EPS: float = 0.05
APPROX_PRECISION: float = 0.03


def find_modal(grayscale: Image, verbose: int = 0) -> BoundingBox | None:
    result: BoundingBox | None = None
    preview: Image | None = None
    source_height, source_width = grayscale.shape[:2]

    try:
        binary: Image = cv2.threshold(grayscale, 0, 255, cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if verbose >= VERBOSE_IMAGE:
            preview = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        for contour in contours:
            epsilon: float = APPROX_PRECISION * cv2.arcLength(contour, True)  # type: ignore
            approx = cv2.approxPolyDP(contour, epsilon, True)  # type: ignore
            if preview is not None:
                cv2.drawContours(preview, [approx], -1, (0, 0, 255))

            rect: Sequence[int] = cv2.boundingRect(approx)  # type: ignore
            [left, top, width, height] = rect

            aspect_ratio: float = width / height
            if (
                width > source_width / 2
                and abs(aspect_ratio - RESULT_ASPECT_RATIO) < ASPECT_RATIO_EPS
            ):
                result = BoundingBox(
                    left=left, top=top, right=left + width, bottom=top + height
                )
    except Exception as e:  # catch all errors from opencv
        logger.error(e)

    logger.debug(f"<Modal> => {result}")

    if preview is not None:
        show_image(preview)

    return (
        sanitize_roi(result, image_width=source_width, image_height=source_height)
        if result is not None
        else None
    )
