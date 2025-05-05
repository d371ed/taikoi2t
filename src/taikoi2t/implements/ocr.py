from typing import Iterable, List

from cv2 import rectangle

from taikoi2t.implements.image import show_image
from taikoi2t.models.image import Image
from taikoi2t.models.ocr import Character


def join_chars(chars: Iterable[Character]) -> str:
    return "".join(c[1] for c in chars).replace(" ", "")


# for debug
def show_detection_result(image: Image, chars: List[Character]) -> None:
    title: str = ""
    for char in chars:
        rectangle(image, char[0][0], char[0][2], 0, 1)
        title += char[1]
    show_image(image, title)
