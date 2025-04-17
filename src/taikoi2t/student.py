from itertools import chain
from typing import Dict, Iterable, List, Sequence, Tuple

type Strikers = Tuple[str, str, str, str]
type Specials = Tuple[str, str]


def split_team(students: Sequence[str]) -> Tuple[Strikers, Specials]:
    ss: Sequence[str] = (
        list(chain(students, [""] * (6 - len(students))))
        if len(students) < 6
        else students
    )
    return (
        (ss[0], ss[1], ss[2], ss[3]),
        (ss[4], ss[5]),
    )


def sort_specials(specials: Specials, ordered_students: Sequence[str]) -> Specials:
    return (
        (specials[1], specials[0])
        if ordered_students.index(specials[0]) > ordered_students.index(specials[1])
        else (specials[0], specials[1])
    )


def apply_alias(names: Iterable[str], mapping: Dict[str, str]) -> List[str]:
    return [(name if mapping[name] == "" else mapping[name]) for name in names]


def normalize_student_name(name: str) -> str:
    return name.replace("(", "（").replace(")", "）")
