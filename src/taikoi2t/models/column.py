from dataclasses import dataclass
from typing import Callable, List, Literal, Sequence, Set, TypeAlias, get_args

from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student

__Requirement: TypeAlias = Literal["students", "opponent", "win_or_lose"]
type Requirement = __Requirement

ALL_REQUIREMENTS: Set[Requirement] = set(get_args(__Requirement))

type ColumnSelector = Callable[[MatchResult], List[str | Student]]


@dataclass(frozen=True)
class Column:
    keys: Sequence[str]
    requirement: Requirement | None
    selector: ColumnSelector
