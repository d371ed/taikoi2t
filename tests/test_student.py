import logging

import pytest

from taikoi2t.application.student import STUDENTS_LEFT_XS, StudentDictionaryImpl
from taikoi2t.implements.student import (
    normalize_student_name,
    remove_diacritics,
)
from taikoi2t.models.student import Student


def test_StudentDictionary_match() -> None:
    dic = StudentDictionaryImpl(
        [
            ("シロコ（水着）", "水シロコ"),
            ("ホシノ", ""),
            ("ヒビキ", ""),
            ("シロコ＊テラー", "シロコ＊"),
            ("シロコ（ライディング）", "ラシロコ"),
            ("シロコ", ""),
            ("ネル（バニーガール）", "バネル"),
            ("ネル", ""),
            ("ネル（制服）", "制ネル"),
            ("キサキ", ""),
            ("ナギサ", ""),
            ("サキ", ""),
        ]
    )
    assert dic.match("ホシノ") == Student(1, "ホシノ", None)
    assert dic.match("シロコ") == Student(5, "シロコ", None)
    assert dic.match("シロコ（水着）") == Student(0, "シロコ（水着）", "水シロコ")
    assert dic.match("シロコ（水着") == Student(0, "シロコ（水着）", "水シロコ")
    assert dic.match("シロコ水者") == Student(
        -1, "Error", None
    )  # cannot match this correctly
    assert dic.match("シロコ＊テラー") == Student(3, "シロコ＊テラー", "シロコ＊")
    assert dic.match("シロコミテラー") == Student(3, "シロコ＊テラー", "シロコ＊")
    assert dic.match("ネル（ハニーカール）") == Student(
        6, "ネル（バニーガール）", "バネル"
    )
    assert dic.match("ナキサ") == Student(10, "ナギサ", None)


def test_StudentDictionary_validate_valid(caplog: pytest.LogCaptureFixture) -> None:
    dic = StudentDictionaryImpl(
        [
            ("シロコ（水着）", "水シロコ"),
            ("ホシノ", ""),
        ]
    )
    assert dic.validate() is True
    assert caplog.record_tuples == []


def test_StudentDictionary_validate_duplicated_names(
    caplog: pytest.LogCaptureFixture,
) -> None:
    dic = StudentDictionaryImpl(
        [
            ("シロコ（水着）", "水シロコ"),
            ("ホシノ", ""),
            ("シロコ（水着）", ""),
        ]
    )
    assert dic.validate() is True  # warning is valid
    assert caplog.record_tuples == [
        (
            "taikoi2t.student.StudentDictionary",
            logging.WARNING,
            "Duplicated names in student's dictionary ['シロコ（水着）']",
        )
    ]


def test_normalize_student_name() -> None:
    res1 = normalize_student_name("シロコ(水着)")
    assert res1 == "シロコ（水着）"


def test_remove_diacritics() -> None:
    res1 = remove_diacritics("シロコ（水着）")
    assert res1 == "シロコ（水着）"

    res2 = remove_diacritics("ナギサ")
    assert res2 == "ナキサ"

    res3 = remove_diacritics("ノア（パジャマ）")
    assert res3 == "ノア（ハシャマ）"


def test_STUDENTS_LEFT_XS() -> None:
    assert len(list(STUDENTS_LEFT_XS)) == 12
