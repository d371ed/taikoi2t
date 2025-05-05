from dataclasses import dataclass
from typing import List, Optional

from taikoi2t.models.student import Student


@dataclass(frozen=True)
class Strikers:
    striker1: Student
    striker2: Student
    striker3: Student
    striker4: Student

    def list(self) -> List[Student]:
        return [self.striker1, self.striker2, self.striker3, self.striker4]


@dataclass(frozen=True)
class Specials:
    special1: Student
    special2: Student

    def list(self) -> List[Student]:
        return [self.special1, self.special2]


@dataclass
class Team:
    wins: bool
    owner: Optional[str]
    strikers: Strikers
    specials: Specials
