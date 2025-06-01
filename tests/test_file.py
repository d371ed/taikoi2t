import logging
import textwrap
from pathlib import Path

import cv2
import numpy
import pytest

from taikoi2t.application.file import expand_paths, read_student_dictionary_source_file
from taikoi2t.models.image import Image


def test_read_student_dictionary_source_file(tmp_path: Path) -> None:
    content1 = textwrap.dedent("""\
        シロコ（水着）,水シロコ
        ホシノ
        ノノミ,,非遮蔽,750
    """)
    path1 = tmp_path / "students1.csv"
    path1.write_text(content1, encoding="utf-8")

    res1 = read_student_dictionary_source_file(path1)
    assert res1 == [("シロコ（水着）", "水シロコ"), ("ホシノ", ""), ("ノノミ", "")]


def test_read_student_dictionary_source_file_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    content1 = textwrap.dedent("""\
        ,水シロコ

        ホシノ
    """)
    path1 = tmp_path / "students1.csv"
    path1.write_text(content1, encoding="utf-8")

    res1 = read_student_dictionary_source_file(path1)
    assert res1 == [("ホシノ", "")]

    assert caplog.record_tuples == [
        ("taikoi2t.file", logging.WARNING, "Empty name at line 1; ['', '水シロコ']"),
        ("taikoi2t.file", logging.WARNING, "Empty line at line 2"),
    ]


def test_read_student_dictionary_source_file_not_found(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    path1 = tmp_path / "students1.csv"
    res1 = read_student_dictionary_source_file(path1)
    assert res1 is None

    assert len(caplog.record_tuples) == 1
    log1 = caplog.record_tuples[0]
    assert log1[:2] == ("taikoi2t.file", logging.CRITICAL)
    assert "students1.csv is not found" in log1[2]


def test_read_student_dictionary_source_file_empty(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    path1 = tmp_path / "students1.csv"
    path1.write_text("", encoding="utf-8")
    res1 = read_student_dictionary_source_file(path1)
    assert res1 is None

    assert len(caplog.record_tuples) == 1
    log1 = caplog.record_tuples[0]
    assert log1[:2] == ("taikoi2t.file", logging.CRITICAL)
    assert "students1.csv is invalid as student's dictionary" in log1[2]


def test_read_student_dictionary_source_file_not_text(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    image1: Image = numpy.zeros((100, 100, 3), dtype=numpy.uint8)
    path1 = tmp_path / "image1.png"
    cv2.imwrite(path1.as_posix(), image1)
    res1 = read_student_dictionary_source_file(path1)
    assert res1 is None

    assert len(caplog.record_tuples) == 1
    log1 = caplog.record_tuples[0]
    assert log1[:2] == ("taikoi2t.file", logging.CRITICAL)
    assert "image1.png is invalid as an UTF-8 text" in log1[2]


def test_read_student_dictionary_source_file_directory(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    path1 = tmp_path / "dir1"
    path1.mkdir()
    res1 = read_student_dictionary_source_file(path1)
    assert res1 is None

    assert len(caplog.record_tuples) == 1
    log1 = caplog.record_tuples[0]
    assert log1[:2] == ("taikoi2t.file", logging.CRITICAL)
    assert "dir1 is not file" in log1[2]


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
