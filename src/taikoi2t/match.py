from dataclasses import dataclass
from itertools import chain
from typing import Callable, Optional

from taikoi2t.args import Args
from taikoi2t.student import ERROR_STUDENT, Specials, Strikers, StudentDictionary


@dataclass
class MatchResult:
    player_wins: bool
    player_strikers: Strikers
    player_specials: Specials
    opponent: Optional[str]
    opponent_strikers: Strikers
    opponent_specials: Specials

    def render(self, dictionary: StudentDictionary, settings: Args) -> str:
        name_mapping: Callable[[str], str] = (
            dictionary.apply_alias if settings.alias else (lambda n: n)
        )
        sort_specials: Callable[[Specials], Specials] = (
            dictionary.sort_specials if settings.sp_sort else (lambda s: s)
        )
        row = chain(
            ["TRUE" if self.player_wins else "FALSE"],
            (name_mapping(n) for n in self.player_strikers),
            (name_mapping(m) for m in sort_specials(self.player_specials)),
            ([self.opponent or "Error"] if settings.opponent else []),
            (name_mapping(n) for n in self.opponent_strikers),
            (name_mapping(n) for n in sort_specials(self.opponent_specials)),
        )
        return ("," if settings.csv else "\t").join(row)


def new_errored_match_result() -> MatchResult:
    return MatchResult(
        player_wins=False,
        player_strikers=(ERROR_STUDENT, ERROR_STUDENT, ERROR_STUDENT, ERROR_STUDENT),
        player_specials=(ERROR_STUDENT, ERROR_STUDENT),
        opponent=None,
        opponent_strikers=(ERROR_STUDENT, ERROR_STUDENT, ERROR_STUDENT, ERROR_STUDENT),
        opponent_specials=(ERROR_STUDENT, ERROR_STUDENT),
    )
