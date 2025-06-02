import json
from typing import Sequence

from taikoi2t.application.column import COLUMN_DICTIONARY, DEFAULT_COLUMN_KEYS
from taikoi2t.implements.match import render_match
from taikoi2t.models.args import VERBOSE_SILENT
from taikoi2t.models.column import Column
from taikoi2t.models.image import BoundingBox, ImageMeta
from taikoi2t.models.match import MatchResult
from taikoi2t.models.settings import OutputFormat, Settings
from taikoi2t.models.student import Student
from taikoi2t.models.team import Specials, Strikers, Team

__S1 = Student(1, "シロコ（水着）", "水シロコ")
__S2 = Student(2, "ホシノ", None)
__S3 = Student(3, "ミヤコ", None)
__S4 = Student(4, "シロコ＊テラー", "シロコ＊")
__S5 = Student(5, "ノノミ", None)
__S6 = Student(6, "佐天涙子", None)
__S7 = Student(7, "シュン", None)
__S8 = Student(8, "ハナコ（水着）", "水ハナコ")
__S9 = Student(9, "ヒビキ", None)
__MATCH = MatchResult(
    id="1234567890-image0png",
    image=ImageMeta(
        path="path/to/image0.png",
        name="image0.png",
        birth_time_ns=1111,
        modify_time_ns=2222,
        width=1920,
        height=1080,
        modal=BoundingBox(10, 20, 300, 400),
    ),
    player=Team(True, None, Strikers(__S2, __S3, __S4, __S5), Specials(__S1, __S6)),
    opponent=Team(
        False, "対戦相手", Strikers(__S2, __S7, __S4, __S8), Specials(__S9, __S1)
    ),
)

__DEFAULT_COLUMNS = [COLUMN_DICTIONARY[key] for key in DEFAULT_COLUMN_KEYS]


def test_render_match_empty_columns() -> None:
    res1 = render_match(__MATCH, __new_settings(columns=[]))
    assert res1 == ""


def test_render_match_output_format() -> None:
    res1 = render_match(__MATCH, __new_settings(output_format="tsv"))
    assert (
        res1
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )

    res2 = render_match(__MATCH, __new_settings(output_format="csv"))
    assert (
        res2
        == "TRUE,ホシノ,ミヤコ,シロコ＊,ノノミ,水シロコ,佐天涙子,ホシノ,シュン,シロコ＊,水ハナコ,ヒビキ,水シロコ"
    )

    res3 = render_match(__MATCH, __new_settings(output_format="json"))
    assert json.loads(res3)["player"]["strikers"]["striker1"]["name"] == "ホシノ"


def test_render_match_alias() -> None:
    res1 = render_match(__MATCH, __new_settings(alias=True))
    assert (
        res1
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )

    res2 = render_match(__MATCH, __new_settings(alias=False))
    assert (
        res2
        == "TRUE\tホシノ\tミヤコ\tシロコ＊テラー\tノノミ\tシロコ（水着）\t佐天涙子\tホシノ\tシュン\tシロコ＊テラー\tハナコ（水着）\tヒビキ\tシロコ（水着）"
    )


def test_render_match_sp_sort_should_not_affect() -> None:
    res1 = render_match(__MATCH, __new_settings(sp_sort=True))
    assert (
        res1
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )

    res2 = render_match(__MATCH, __new_settings(sp_sort=False))
    assert (
        res2
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\tヒビキ\t水シロコ"
    )


def __new_settings(
    columns: Sequence[Column] = __DEFAULT_COLUMNS,
    output_format: OutputFormat = "tsv",
    alias: bool = True,
    sp_sort: bool = True,
) -> Settings:
    return Settings(
        columns=columns,
        output_format=output_format,
        alias=alias,
        sp_sort=sp_sort,
        verbose=VERBOSE_SILENT,
    )
