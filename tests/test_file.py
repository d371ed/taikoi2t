import textwrap
from pathlib import Path

from taikoi2t.application.file import expand_paths, read_student_dictionary_source_file


def test_read_student_dictionary_source_file(tmp_path: Path) -> None:
    content1 = textwrap.dedent("""\
        シロコ（水着）,水シロコ
        ホシノ,
        ノノミ,
    """)
    path1 = tmp_path / "students1.csv"
    path1.write_text(content1, encoding="utf-8")

    res1 = read_student_dictionary_source_file(path1)
    assert res1 == [("シロコ（水着）", "水シロコ"), ("ホシノ", ""), ("ノノミ", "")]


def test_expand_paths(tmp_path: Path) -> None:
    for name in ["test1.png", "test2.png", "test10.png", "test3.jpg", "unrelated.txt"]:
        (tmp_path / name).touch()

    res1 = expand_paths(
        [tmp_path / "*.png", tmp_path / "test1.png", tmp_path / "*.jpg"]
    )
    assert res1 == [
        tmp_path / "test1.png",
        tmp_path / "test10.png",  # sort by name
        tmp_path / "test2.png",
        tmp_path / "test1.png",
        tmp_path / "test3.jpg",
    ]
