from taikoi2t.implements.student import new_empty_student, new_error_student
from taikoi2t.implements.team import new_team_from, sort_specials
from taikoi2t.models.student import Student
from taikoi2t.models.team import Specials, Strikers, Team


def test_new_team_from() -> None:
    student1 = Student(1, "ホシノ", None)
    student2 = Student(2, "ミヤコ", None)
    student3 = Student(3, "シロコ＊テラー", "シロコ＊")
    student4 = Student(4, "ノノミ", None)
    student5 = Student(5, "シロコ（水着）", "水シロコ")
    student6 = Student(6, "佐天涙子", None)
    student7 = Student(7, "レイサ", None)
    empty = new_empty_student()

    assert new_team_from(
        [student1, student2, student3, student4, student5, student6]
    ) == Team(
        False,
        None,
        Strikers(student1, student2, student3, student4),
        Specials(student5, student6),
    )

    assert new_team_from(
        [student1, student2, student3, student4, student5, student6, student7]
    ) == Team(
        False,
        None,
        Strikers(student1, student2, student3, student4),
        Specials(student5, student6),
    )

    assert new_team_from([student1, student2, student3, student4, student5]) == Team(
        False,
        None,
        Strikers(student1, student2, student3, student4),
        Specials(student5, empty),
    )

    assert new_team_from([student1, student2, student3]) == Team(
        False,
        None,
        Strikers(student1, student2, student3, empty),
        Specials(empty, empty),
    )

    assert new_team_from([]) == Team(
        False, None, Strikers(empty, empty, empty, empty), Specials(empty, empty)
    )


def test_sort_specials() -> None:
    student1 = Student(1, "シロコ（水着）", "水シロコ")
    student2 = Student(2, "ヒビキ", None)
    student3 = Student(3, "サツキ", None)
    errored = new_error_student()
    empty = new_empty_student()

    assert sort_specials(Specials(student1, student2)) == Specials(student1, student2)
    assert sort_specials(Specials(student2, student1)) == Specials(student1, student2)
    assert sort_specials(Specials(student3, student1)) == Specials(student1, student3)

    assert sort_specials(Specials(student2, errored)) == Specials(student2, errored)
    assert sort_specials(Specials(errored, student2)) == Specials(student2, errored)

    assert sort_specials(Specials(student2, empty)) == Specials(student2, empty)
    assert sort_specials(Specials(empty, student2)) == Specials(student2, empty)

    assert sort_specials(Specials(errored, empty)) == Specials(errored, empty)
    assert sort_specials(Specials(empty, errored)) == Specials(errored, empty)

    assert sort_specials(Specials(errored, errored)) == Specials(errored, errored)
    assert sort_specials(Specials(empty, empty)) == Specials(empty, empty)
