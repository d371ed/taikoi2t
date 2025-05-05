from typing import List

from taikoi2t.implements.ocr import join_chars
from taikoi2t.models.ocr import Character


def test_join_chars() -> None:
    chars1: List[Character] = [
        ([(23, 10), (149, 10), (149, 55), (23, 55)], "シロコ", 0.9999086002751579),
        ([(169, 6), (236, 6), (236, 57), (169, 57)], "(水", 0.9998506348363045),
        ([(92, 53), (156, 53), (156, 104), (92, 104)], " 着)", 0.9454015234870539),
    ]
    assert join_chars(chars1) == "シロコ(水着)"

    char2: List[Character] = [
        ([(63, 6), (191, 6), (191, 56), (63, 56)], "ヒ ビキ", 0.9983293100557972)
    ]
    assert join_chars(char2) == "ヒビキ"

    char3: List[Character] = []
    assert join_chars(char3) == ""
