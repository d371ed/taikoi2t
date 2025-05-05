from dataclasses import dataclass
from typing import Callable, List, Literal, Sequence

from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student

type Requirement = Literal["students", "opponent", "win_or_lose"]

type ColumnSelector = Callable[[MatchResult], List[str | Student]]


@dataclass(frozen=True)
class Column:
    keys: Sequence[str]
    requirement: Requirement | None
    selector: ColumnSelector
