from taikoi2t.student import Specials, Strikers, Student, new_empty_student
from taikoi2t.team import Team, new_team_from


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
