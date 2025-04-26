from typing import Iterable, List, Tuple

from cv2 import rectangle

from taikoi2t.image import Image, show_image

type Character = Tuple[List[Tuple[int, int]], str, float]


def join_chars(chars: Iterable[Character]) -> str:
    return "".join(c[1] for c in chars).replace(" ", "")


# for debug
def show_detection_result(image: Image, chars: List[Character]) -> None:
    title: str = ""
    for char in chars:
        rectangle(image, char[0][0], char[0][2], 0, 1)
        title += char[1]
    show_image(image, title)
