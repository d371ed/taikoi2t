from itertools import chain
from typing import Sequence

from taikoi2t.implements.student import new_empty_student, new_error_student
from taikoi2t.models.student import ERROR_STUDENT_NAME, Student
from taikoi2t.models.team import Specials, Strikers, Team

__STUDENT_COUNT_IN_TEAM: int = 6


def new_team_from(students: Sequence[Student]) -> Team:
    ss: Sequence[Student]
    if len(students) < __STUDENT_COUNT_IN_TEAM:
        fillers = map(
            lambda _: new_empty_student(),
            range(__STUDENT_COUNT_IN_TEAM - len(students)),
        )
        ss = list(chain(students, fillers))
    else:
        ss = students

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


def sort_specials(specials: Specials) -> Specials:
    sp1_is_valid = specials.special1.index >= 0
    sp2_is_valid = specials.special2.index >= 0

    if (
        sp1_is_valid
        and sp2_is_valid
        and specials.special1.index > specials.special2.index
    ):
        return specials.swapped()
    elif not sp1_is_valid and sp2_is_valid:
        return specials.swapped()
    elif (
        not sp1_is_valid
        and not sp2_is_valid
        and specials.special1.name != ERROR_STUDENT_NAME
    ):
        # sp1 is empty (maybe) -> right
        return specials.swapped()
    else:
        return specials
