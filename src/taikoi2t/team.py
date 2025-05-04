from dataclasses import dataclass
from itertools import chain
from typing import Optional, Sequence

from taikoi2t.student import (
    Specials,
    Strikers,
    Student,
    new_empty_student,
    new_error_student,
)


@dataclass
class Team:
    # side: str # TODO: "attack" | "defense"
    wins: bool
    owner: Optional[str]
    strikers: Strikers
    specials: Specials


def new_team_from(student_list: Sequence[Student]) -> Team:
    ss: Sequence[Student] = (
        list(
            chain(
                student_list,
                map(lambda _: new_empty_student(), range(6 - len(student_list))),
            )
        )
        if len(student_list) < 6
        else student_list
    )
    return Team(
        False, None, Strikers(ss[0], ss[1], ss[2], ss[3]), Specials(ss[4], ss[5])
    )


def new_error_team() -> Team:
    return Team(
        wins=False,
        owner="Error",
        strikers=Strikers(
            new_error_student(),
            new_error_student(),
            new_error_student(),
            new_error_student(),
        ),
        specials=Specials(new_error_student(), new_error_student()),
    )
