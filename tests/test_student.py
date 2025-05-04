from taikoi2t.student import (
    Specials,
    Student,
    StudentDictionary,
    new_empty_student,
    new_error_student,
    normalize_student_name,
    remove_diacritics,
)


def test_Specials_sort() -> None:
    student1 = Student(1, "シロコ（水着）", "水シロコ")
    student2 = Student(2, "ヒビキ", None)
    student3 = Student(3, "サツキ", None)
    errored = new_error_student()
    empty = new_empty_student()

    assert Specials(student1, student2).sort() == Specials(student1, student2)
    assert Specials(student2, student1).sort() == Specials(student1, student2)
    assert Specials(student3, student1).sort() == Specials(student1, student3)

    assert Specials(student2, errored).sort() == Specials(student2, errored)
    assert Specials(errored, student2).sort() == Specials(student2, errored)

    assert Specials(student2, empty).sort() == Specials(student2, empty)
    assert Specials(empty, student2).sort() == Specials(student2, empty)

    assert Specials(errored, empty).sort() == Specials(errored, empty)
    assert Specials(empty, errored).sort() == Specials(errored, empty)

    assert Specials(errored, errored).sort() == Specials(errored, errored)
    assert Specials(empty, empty).sort() == Specials(empty, empty)


def test_StudentDictionary_match() -> None:
    dic = StudentDictionary(
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
    # assert dic.match("シロコ水者") == Student(0, "シロコ（水着）", "水シロコ") # cannot match this correctly
    assert dic.match("シロコ＊テラー") == Student(3, "シロコ＊テラー", "シロコ＊")
    assert dic.match("シロコミテラー") == Student(3, "シロコ＊テラー", "シロコ＊")
    assert dic.match("ネル（ハニーカール）") == Student(
        6, "ネル（バニーガール）", "バネル"
    )
    assert dic.match("ナキサ") == Student(10, "ナギサ", None)


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
