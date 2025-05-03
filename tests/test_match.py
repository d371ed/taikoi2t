from pathlib import Path

from taikoi2t.args import VERBOSE_SILENT, Args
from taikoi2t.match import MatchResult
from taikoi2t.student import StudentDictionary


def test_MatchResult_render() -> None:
    match = MatchResult(
        player_wins=True,
        player_strikers=("ホシノ", "ミヤコ", "シロコ＊テラー", "ノノミ"),
        player_specials=("シロコ（水着）", "佐天涙子"),
        opponent="対戦相手",
        opponent_strikers=("ホシノ", "シュン", "シロコ＊テラー", "ハナコ（水着）"),
        opponent_specials=("シロコ（水着）", "ヒビキ"),
    )
    dic = StudentDictionary(
        [
            ("ホシノ", ""),
            ("ミヤコ", ""),
            ("シロコ＊テラー", "シロコ＊"),
            ("ノノミ", ""),
            ("シロコ（水着）", "水シロコ"),
            ("佐天涙子", ""),
            ("シュン", ""),
            ("ハナコ（水着）", "水ハナコ"),
            ("ヒビキ", ""),
        ]
    )

    res1 = match.render(dic, __new_settings(opponent=False, csv=False, noAlias=False))
    assert (
        res1
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\tホシノ\tシュン\tシロコ＊\t水ハナコ\t水シロコ\tヒビキ"
    )

    res2 = match.render(dic, __new_settings(opponent=True, csv=False, noAlias=False))
    assert (
        res2
        == "TRUE\tホシノ\tミヤコ\tシロコ＊\tノノミ\t水シロコ\t佐天涙子\t対戦相手\tホシノ\tシュン\tシロコ＊\t水ハナコ\t水シロコ\tヒビキ"
    )

    res3 = match.render(dic, __new_settings(opponent=False, csv=True, noAlias=False))
    assert (
        res3
        == "TRUE,ホシノ,ミヤコ,シロコ＊,ノノミ,水シロコ,佐天涙子,ホシノ,シュン,シロコ＊,水ハナコ,水シロコ,ヒビキ"
    )

    res4 = match.render(dic, __new_settings(opponent=False, csv=False, noAlias=True))
    assert (
        res4
        == "TRUE\tホシノ\tミヤコ\tシロコ＊テラー\tノノミ\tシロコ（水着）\t佐天涙子\tホシノ\tシュン\tシロコ＊テラー\tハナコ（水着）\tシロコ（水着）\tヒビキ"
    )


def __new_settings(opponent: bool, csv: bool, noAlias: bool) -> Args:
    return Args(
        dictionary=Path("dict.csv"),
        opponent=opponent,
        csv=csv,
        no_alias=noAlias,
        verbose=VERBOSE_SILENT,
        files=[],
    )
