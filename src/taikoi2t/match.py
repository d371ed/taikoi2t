import json
from dataclasses import asdict, dataclass
from itertools import chain

from taikoi2t.image import ImageMeta
from taikoi2t.settings import Settings
from taikoi2t.student import (
    Student,
)
from taikoi2t.team import Team, new_error_team


@dataclass
class MatchResult:
    image: ImageMeta
    player: Team
    opponent: Team

    def render(self, settings: Settings) -> str:
        if settings.output_format == "json":
            return json.dumps(asdict(self), ensure_ascii=False)

        def select_name(s: Student) -> str:
            return s.alias or s.name if settings.alias else s.name

        row = chain(
            ["TRUE" if self.player.wins else "FALSE"],
            (select_name(s) for s in self.player.strikers.list()),
            (select_name(s) for s in self.player.specials.list()),
            ([self.opponent.owner or "Error"] if settings.opponent else []),
            (select_name(s) for s in self.opponent.strikers.list()),
            (select_name(s) for s in self.opponent.specials.list()),
        )
        return ("," if settings.output_format == "csv" else "\t").join(row)


def new_errored_match_result(image: ImageMeta) -> MatchResult:
    return MatchResult(image, new_error_team(), new_error_team())
