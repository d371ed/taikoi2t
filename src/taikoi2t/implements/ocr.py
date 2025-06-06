import logging
from typing import Iterable, Sequence

import easyocr  # type: ignore

from taikoi2t.implements.image import crop
from taikoi2t.models.image import BoundingBox, Image
from taikoi2t.models.ocr import Character

logger: logging.Logger = logging.getLogger("taikoi2t.ocr")


def read_text_from_roi(
    reader: easyocr.Reader, source: Image, roi: BoundingBox
) -> str | None:
    cropped: Image = crop(source, roi)
    try:
        chars: Sequence[Character] = reader.readtext(cropped)  # type: ignore
        return join_chars(chars) if len(chars) > 0 else None
    except Exception as e:  # catch errors from easyocr and opencv
        logger.error(e)
        return None


def join_chars(chars: Iterable[Character]) -> str:
    return "".join(c[1] for c in chars).replace(" ", "")
