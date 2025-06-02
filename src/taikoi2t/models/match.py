from dataclasses import dataclass

from taikoi2t.models.image import ImageMeta
from taikoi2t.models.team import Team


@dataclass(frozen=True)
class MatchResult:
    id: str
    image: ImageMeta
    player: Team
    opponent: Team
