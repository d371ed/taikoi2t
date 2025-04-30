import pytest

from taikoi2t.student import (
    StudentDictionary,
    normalize_student_name,
    remove_diacritics,
    split_team,
)


def test_StudentDictionary_match() -> None:
    dic = StudentDictionary(
        [
            ("シロコ（水着）", "水シロコ"),
            ("ホシノ", ""),
            ("ヒビキ", ""),
            ("シロコ＊テラー", "シロコ＊"),
            ("佐天涙子", ""),
            ("ノノミ", ""),
            ("シロコ（ライディング）", "ラシロコ"),
            ("シロコ", ""),
            ("ネル（バニーガール）", "バネル"),
            ("ネル", ""),
            ("ネル（制服）", "制ネル"),
            ("キサキ", ""),
            ("ナギサ", ""),
            ("サキ", ""),
            ("シュン", ""),
            ("アヤネ（水着）", "水アヤネ"),
            ("ジュリ（アルバイト）", "アジュリ"),
            ("ジュリ", ""),
        ]
    )
    assert dic.match("ホシノ") == "ホシノ"
    assert dic.match("シロコ") == "シロコ"
    assert dic.match("シロコ（水着）") == "シロコ（水着）"
    assert dic.match("シロコ（水着") == "シロコ（水着）"
    # assert dic.match("シロコ水者") == "シロコ（水着）" # cannot match this correctly
    assert dic.match("シロコ＊テラー") == "シロコ＊テラー"
    assert dic.match("シロコミテラー") == "シロコ＊テラー"
    assert dic.match("ネル（ハニーカール）") == "ネル（バニーガール）"
    assert dic.match("ナキサ") == "ナギサ"


def test_StudentDictionary_arrange_team() -> None:
    dic = StudentDictionary(
        [
            ("シロコ（水着）", "水シロコ"),
            ("ホシノ", ""),
            ("ヒビキ", ""),
            ("シロコ＊テラー", "シロコ＊"),
            ("佐天涙子", ""),
            ("ノノミ", ""),
            ("ネル（バニーガール）", "バネル"),
            ("シュン", ""),
            ("アヤネ（水着）", "水アヤネ"),
        ]
    )
    res1 = dic.arrange_team(
        [
            "ホシノ",
            "ネル（バニーガール）",
            "シロコ＊テラー",
            "ノノミ",
            "アヤネ（水着）",
            "シロコ（水着）",
        ]
    )
    assert res1 == ["ホシノ", "バネル", "シロコ＊", "ノノミ", "水シロコ", "水アヤネ"]


def test_StudentDictionary_apply_alias() -> None:
    dic = StudentDictionary(
        [
            ("シロコ（水着）", "水シロコ"),
            ("ホシノ", ""),
            ("ヒビキ", ""),
            ("佐天涙子", ""),
        ]
    )

    assert dic.apply_alias(("シロコ（水着）", "ヒビキ")) == ["水シロコ", "ヒビキ"]

    with pytest.raises(KeyError) as e:
        dic.apply_alias(("シロコ（水着）", "サツキ"))
    assert str(e.value) == "'サツキ'"


def test_StudentDictionary_sort_specials() -> None:
    dic = StudentDictionary(
        [("シロコ（水着）", ""), ("ホシノ", ""), ("ヒビキ", ""), ("佐天涙子", "")]
    )

    assert dic.sort_specials(("シロコ（水着）", "ヒビキ")) == (
        "シロコ（水着）",
        "ヒビキ",
    )
    assert dic.sort_specials(("ヒビキ", "シロコ（水着）")) == (
        "シロコ（水着）",
        "ヒビキ",
    )
    assert dic.sort_specials(("シロコ（水着）", "サツキ")) == (
        "シロコ（水着）",
        "Error",
    )
    assert dic.sort_specials(("ウタハ", "ヒビキ")) == ("ヒビキ", "Error")
    assert dic.sort_specials(("シロコ（水着）", "")) == ("シロコ（水着）", "")
    assert dic.sort_specials(("", "")) == ("", "")
    assert dic.sort_specials(("ノドカ（温泉）", "")) == ("Error", "")
    assert dic.sort_specials(("", "ノドカ（温泉）")) == ("Error", "")


def test_split_team() -> None:
    st1, sp1 = split_team(
        ["ホシノ", "シュン", "シロコ＊テラー", "レイサ", "ヒビキ", "シロコ（水着）"]
    )
    assert st1 == ("ホシノ", "シュン", "シロコ＊テラー", "レイサ")
    assert sp1 == ("ヒビキ", "シロコ（水着）")

    st2, sp2 = split_team(["ユウカ", "ノドカ（温泉）", "マリー"])
    assert st2 == ("ユウカ", "ノドカ（温泉）", "マリー", "")
    assert sp2 == ("", "")

    st3, sp3 = split_team([])
    assert st3 == ("", "", "", "")
    assert sp3 == ("", "")


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
