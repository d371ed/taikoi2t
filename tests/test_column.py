from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Sequence

from taikoi2t.application.column import COLUMN_DICTIONARY, COLUMNS
from taikoi2t.models.image import ImageMeta
from taikoi2t.models.match import MatchResult
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
    image=ImageMeta("", ""),
    player=Team(True, None, Strikers(__S2, __S3, __S4, __S5), Specials(__S1, __S6)),
    opponent=Team(
        False, "対戦相手", Strikers(__S2, __S7, __S4, __S8), Specials(__S9, __S1)
    ),
)


@dataclass(frozen=True)
class __ColumnCount:
    keys: Sequence[str]
    count: int


def test_COLUMNS_selected_column_count() -> None:
    targets: Iterable[__ColumnCount] = [
        __ColumnCount(
            ["IMAGE_PATH", "IMAGE_NAME", "INAME", "IMAGE_WIDTH", "IMAGE_HEIGHT"], 1
        ),
        __ColumnCount(["PLAYER_WINS", "LEFT_WINS", "PWIN", "LWIN"], 1),
        __ColumnCount(["PLAYER_WOL", "LEFT_WOL", "PWOL", "LWOL"], 1),
        __ColumnCount(
            ["PLAYER_NAME", "PLAYER_OWNER", "LEFT_OWNER", "PNAME", "POWN", "LOWN"], 1
        ),
        __ColumnCount(
            [
                "PLAYER_TEAM",
                "LEFT_TEAM",
                "PLAYER_MEMBERS",
                "LEFT_MEMBERS",
                "PTEAM",
                "LTEAM",
                "PMEMS",
                "LMEMS",
            ],
            6,
        ),
        __ColumnCount(["PLAYER_STRIKERS", "LEFT_STRIKERS", "PSTS", "LSTS"], 4),
        __ColumnCount(
            ["PLAYER_STRIKER_1", "LEFT_STRIKER_1", "PST1", "LST1", "P1", "L1"], 1
        ),
        __ColumnCount(
            ["PLAYER_STRIKER_2", "LEFT_STRIKER_2", "PST2", "LST2", "P2", "L2"], 1
        ),
        __ColumnCount(
            ["PLAYER_STRIKER_3", "LEFT_STRIKER_3", "PST3", "LST3", "P3", "L3"], 1
        ),
        __ColumnCount(
            ["PLAYER_STRIKER_4", "LEFT_STRIKER_4", "PST4", "LST4", "P4", "L4"], 1
        ),
        __ColumnCount(["PLAYER_SPECIALS", "LEFT_SPECIALS", "PSPS", "LSPS"], 2),
        __ColumnCount(
            ["PLAYER_SPECIAL_1", "LEFT_SPECIAL_1", "PSP1", "LSP1", "P5", "L5"], 1
        ),
        __ColumnCount(
            ["PLAYER_SPECIAL_2", "LEFT_SPECIAL_2", "PSP2", "LSP2", "P6", "L6"], 1
        ),
        __ColumnCount(["OPPONENT_WINS", "RIGHT_WINS", "OWIN", "RWIN"], 1),
        __ColumnCount(["OPPONENT_WOL", "RIGHT_WOL", "OWOL", "RWOL"], 1),
        __ColumnCount(
            ["OPPONENT_NAME", "OPPONENT_OWNER", "RIGHT_OWNER", "ONAME", "OOWN", "ROWN"],
            1,
        ),
        __ColumnCount(
            [
                "OPPONENT_TEAM",
                "RIGHT_TEAM",
                "OPPONENT_MEMBERS",
                "RIGHT_MEMBERS",
                "OTEAM",
                "RTEAM",
                "OMEMS",
                "RMEMS",
            ],
            6,
        ),
        __ColumnCount(["OPPONENT_STRIKERS", "RIGHT_STRIKERS", "OSTS", "RSTS"], 4),
        __ColumnCount(
            ["OPPONENT_STRIKER_1", "RIGHT_STRIKER_1", "OST1", "RST1", "O1", "R1"], 1
        ),
        __ColumnCount(
            ["OPPONENT_STRIKER_2", "RIGHT_STRIKER_2", "OST2", "RST2", "O2", "R2"], 1
        ),
        __ColumnCount(
            ["OPPONENT_STRIKER_3", "RIGHT_STRIKER_3", "OST3", "RST3", "O3", "R3"], 1
        ),
        __ColumnCount(
            ["OPPONENT_STRIKER_4", "RIGHT_STRIKER_4", "OST4", "RST4", "O4", "R4"], 1
        ),
        __ColumnCount(["OPPONENT_SPECIALS", "RIGHT_SPECIALS", "OSPS", "RSPS"], 2),
        __ColumnCount(
            ["OPPONENT_SPECIAL_1", "RIGHT_SPECIAL_1", "OSP1", "RSP1", "O5", "R5"], 1
        ),
        __ColumnCount(
            ["OPPONENT_SPECIAL_2", "RIGHT_SPECIAL_2", "OSP2", "RSP2", "O6", "R6"], 1
        ),
        __ColumnCount(["BLANK", "BL"], 1),
    ]

    # check all keys contained
    assert set(chain.from_iterable(target.keys for target in targets)) == set(
        chain.from_iterable(column.keys for column in COLUMNS)
    )

    for target in targets:
        for key in target.keys:
            column = COLUMN_DICTIONARY[key]
            assert len(column.selector(__MATCH)) == target.count


def test_COLUMN_DICTIONARY_key_duplication() -> None:
    source_keys = list(chain.from_iterable(column.keys for column in COLUMNS))
    assert len(source_keys) == len(COLUMN_DICTIONARY.keys())
