import json

from taikoi2t.args import VERBOSE_SILENT
from taikoi2t.image import ImageMeta
from taikoi2t.match import MatchResult
from taikoi2t.settings import OutputFormat, Settings
from taikoi2t.student import Specials, Strikers, Student
from taikoi2t.team import Team


def test_MatchResult_render() -> None:
    student1 = Student(1, "シロコ（水着）", "水シロコ")
    student2 = Student(2, "ホシノ", None)
    student3 = Student(3, "ミヤコ", None)
    student4 = Student(4, "シロコ＊テラー", "シロコ＊")
    student5 = Student(5, "ノノミ", None)
    student6 = Student(6, "佐天涙子", None)
    student7 = Student(7, "シュン", None)
    student8 = Student(8, "ハナコ（水着）", "水ハナコ")
    student9 = Student(9, "ヒビキ", None)
    match = MatchResult(
        image=ImageMeta("", ""),
        player=Team(
            True,
            None,
            Strikers(student2, student3, student4, student5),
            Specials(student1, student6),
        ),
        opponent=Team(
            True,
            "対戦相手",
            Strikers(student2, student7, student4, student8),
            Specials(student9, student1),
        ),
    )

    # sp_sort does not affect here
    res1 = match.render(__new_settings(sp_sort=True))  # default
    assert (
        res1
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )

    res2 = match.render(__new_settings(opponent=True))
    assert (
        res2
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\t対戦相手\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )

    res3 = match.render(__new_settings(output_format="csv"))
    assert (
        res3
        == "TRUE,ホシノ,ミヤコ,シロコ＊,ノノミ,水シロコ,佐天涙子,ホシノ,シュン,シロコ＊,水ハナコ,ヒビキ,水シロコ"
    )

    res4 = match.render(__new_settings(output_format="json"))
    assert json.loads(res4)["player"]["strikers"]["striker1"]["name"] == "ホシノ"

    res5 = match.render(__new_settings(alias=False))
    assert (
        res5
        == "TRUE\tホシノ\tミヤコ\tシロコ＊テラー\tノノミ\tシロコ（水着）\t佐天涙子\tホシノ\tシュン\tシロコ＊テラー\tハナコ（水着）\tヒビキ\tシロコ（水着）"
    )

    # sp_sort does not affect here
    res6 = match.render(__new_settings(sp_sort=False))
    assert (
        res6
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )


def __new_settings(
    opponent: bool = False,
    output_format: OutputFormat = "tsv",
    alias: bool = True,
    sp_sort: bool = True,
) -> Settings:
    return Settings(
        opponent=opponent,
        output_format=output_format,
        alias=alias,
        sp_sort=sp_sort,
        verbose=VERBOSE_SILENT,
    )
