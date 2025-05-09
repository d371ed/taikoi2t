from itertools import chain
from typing import Dict, Sequence

from taikoi2t.models.column import Column

DEFAULT_COLUMN_KEYS: Sequence[str] = ["PLAYER_WINS", "PLAYER_TEAM", "OPPONENT_TEAM"]
OPPONENT_COLUMN_KEYS: Sequence[str] = [
    "PLAYER_WINS",
    "PLAYER_TEAM",
    "OPPONENT_NAME",
    "OPPONENT_TEAM",
]

COLUMNS: Sequence[Column] = [
    Column(["IMAGE_PATH"], None, lambda m: [m.image.path]),
    Column(["IMAGE_NAME", "INAME"], None, lambda m: [m.image.name]),
    Column(["IMAGE_WIDTH"], None, lambda m: [str(m.image.width)]),
    Column(["IMAGE_HEIGHT"], None, lambda m: [str(m.image.height)]),
    Column(
        ["PLAYER_WINS", "LEFT_WINS", "PWIN", "LWIN"],
        "win_or_lose",
        lambda m: ["TRUE" if m.player.wins else "FALSE"],
    ),
    Column(
        ["PLAYER_WOL", "LEFT_WOL", "PWOL", "LWOL"],
        "win_or_lose",
        lambda m: ["Win" if m.player.wins else "Lose"],
    ),
    Column(
        ["PLAYER_NAME", "PLAYER_OWNER", "LEFT_OWNER", "PNAME", "POWN", "LOWN"],
        "player",
        lambda m: ["Error"] if m.player.owner is None else [m.player.owner],
    ),
    Column(
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
        "students",
        lambda m: [s for s in m.player.strikers.list() + m.player.specials.list()],
    ),
    Column(
        ["PLAYER_STRIKERS", "LEFT_STRIKERS", "PSTS", "LSTS"],
        "students",
        lambda m: [s for s in m.player.strikers.list()],
    ),
    Column(
        ["PLAYER_STRIKER_1", "LEFT_STRIKER_1", "PST1", "LST1", "P1", "L1"],
        "students",
        lambda m: [m.player.strikers.striker1],
    ),
    Column(
        ["PLAYER_STRIKER_2", "LEFT_STRIKER_2", "PST2", "LST2", "P2", "L2"],
        "students",
        lambda m: [m.player.strikers.striker2],
    ),
    Column(
        ["PLAYER_STRIKER_3", "LEFT_STRIKER_3", "PST3", "LST3", "P3", "L3"],
        "students",
        lambda m: [m.player.strikers.striker3],
    ),
    Column(
        ["PLAYER_STRIKER_4", "LEFT_STRIKER_4", "PST4", "LST4", "P4", "L4"],
        "students",
        lambda m: [m.player.strikers.striker4],
    ),
    Column(
        ["PLAYER_SPECIALS", "LEFT_SPECIALS", "PSPS", "LSPS"],
        "students",
        lambda m: [s for s in m.player.specials.list()],
    ),
    Column(
        ["PLAYER_SPECIAL_1", "LEFT_SPECIAL_1", "PSP1", "LSP1", "P5", "L5"],
        "students",
        lambda m: [m.player.specials.special1],
    ),
    Column(
        ["PLAYER_SPECIAL_2", "LEFT_SPECIAL_2", "PSP2", "LSP2", "P6", "L6"],
        "students",
        lambda m: [m.player.specials.special2],
    ),
    Column(
        ["OPPONENT_WINS", "RIGHT_WINS", "OWIN", "RWIN"],
        "win_or_lose",
        lambda m: ["TRUE" if m.opponent.wins else "FALSE"],
    ),
    Column(
        ["OPPONENT_WOL", "RIGHT_WOL", "OWOL", "RWOL"],
        "win_or_lose",
        lambda m: ["Win" if m.opponent.wins else "Lose"],
    ),
    Column(
        ["OPPONENT_NAME", "OPPONENT_OWNER", "RIGHT_OWNER", "ONAME", "OOWN", "ROWN"],
        "opponent",
        lambda m: ["Error"] if m.opponent.owner is None else [m.opponent.owner],
    ),
    Column(
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
        "students",
        lambda m: [s for s in m.opponent.strikers.list() + m.opponent.specials.list()],
    ),
    Column(
        ["OPPONENT_STRIKERS", "RIGHT_STRIKERS", "OSTS", "RSTS"],
        "students",
        lambda m: [s for s in m.opponent.strikers.list()],
    ),
    Column(
        ["OPPONENT_STRIKER_1", "RIGHT_STRIKER_1", "OST1", "RST1", "O1", "R1"],
        "students",
        lambda m: [m.opponent.strikers.striker1],
    ),
    Column(
        ["OPPONENT_STRIKER_2", "RIGHT_STRIKER_2", "OST2", "RST2", "O2", "R2"],
        "students",
        lambda m: [m.opponent.strikers.striker2],
    ),
    Column(
        ["OPPONENT_STRIKER_3", "RIGHT_STRIKER_3", "OST3", "RST3", "O3", "R3"],
        "students",
        lambda m: [m.opponent.strikers.striker3],
    ),
    Column(
        ["OPPONENT_STRIKER_4", "RIGHT_STRIKER_4", "OST4", "RST4", "O4", "R4"],
        "students",
        lambda m: [m.opponent.strikers.striker4],
    ),
    Column(
        ["OPPONENT_SPECIALS", "RIGHT_SPECIALS", "OSPS", "RSPS"],
        "students",
        lambda m: [s for s in m.opponent.specials.list()],
    ),
    Column(
        ["OPPONENT_SPECIAL_1", "RIGHT_SPECIAL_1", "OSP1", "RSP1", "O5", "R5"],
        "students",
        lambda m: [m.opponent.specials.special1],
    ),
    Column(
        ["OPPONENT_SPECIAL_2", "RIGHT_SPECIAL_2", "OSP2", "RSP2", "O6", "R6"],
        "students",
        lambda m: [m.opponent.specials.special2],
    ),
]


COLUMN_DICTIONARY: Dict[str, Column] = dict(
    chain.from_iterable([(key, column) for key in column.keys] for column in COLUMNS)
)
