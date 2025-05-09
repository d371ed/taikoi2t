from typing import Iterable, List, Sequence

import cv2
import easyocr  # type: ignore

from taikoi2t.implements.image import crop, show_image
from taikoi2t.models.image import BoundingBox, Image
from taikoi2t.models.ocr import Character


def read_text_from_roi(
    reader: easyocr.Reader, source: Image, roi: BoundingBox
) -> str | None:
    cropped: Image = crop(source, roi)
    chars: Sequence[Character] = reader.readtext(cropped)  # type: ignore
    return join_chars(chars) if len(chars) > 0 else None


def join_chars(chars: Iterable[Character]) -> str:
    return "".join(c[1] for c in chars).replace(" ", "")


# for debug
def show_detection_result(image: Image, chars: List[Character]) -> None:
    title: str = ""
    for char in chars:
        cv2.rectangle(image, char[0][0], char[0][2], 0, 1)
        title += char[1]
    show_image(image, title)
