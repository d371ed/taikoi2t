from dataclasses import dataclass
from typing import List

from taikoi2t.models.match import MatchResult


@dataclass
class RunResult:
    arguments: List[str]
    starts_at: str
    ends_at: str
    matches: List[MatchResult]
