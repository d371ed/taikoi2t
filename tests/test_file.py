import logging
import textwrap
import time
from pathlib import Path
from typing import Iterable, List

import cv2
import numpy
import pytest

from taikoi2t.application.file import read_student_dictionary_source_file
from taikoi2t.implements.file import expand_paths, sort_files
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
    assert "dir1 is not a file" in log1[2]


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


def test_sort_files(tmp_path: Path) -> None:
    paths = [tmp_path / n for n in ["e31", "f", "b14", "d22", "c", "a43"]]
    for name in ["b14", "d22", "e31", "a43"]:
        (tmp_path / name).touch()
        time.sleep(0.01)
    for name in ["e31", "d22", "a43", "b14"]:
        (tmp_path / name).write_text("test", encoding="utf-8")
        time.sleep(0.01)

    res1 = sort_files(paths, "BIRTH_ASC")
    assert __to_names(res1) == ["b14", "d22", "e31", "a43", "f", "c"]
    res2 = sort_files(paths, "BIRTH_DESC")
    assert __to_names(res2) == ["a43", "e31", "d22", "b14", "f", "c"]
    res3 = sort_files(paths, "MODIFY_ASC")
    assert __to_names(res3) == ["e31", "d22", "a43", "b14", "f", "c"]
    res4 = sort_files(paths, "MODIFY_DESC")
    assert __to_names(res4) == ["b14", "a43", "d22", "e31", "f", "c"]
    res5 = sort_files(paths, "NAME_ASC")
    assert __to_names(res5) == ["a43", "b14", "c", "d22", "e31", "f"]
    res6 = sort_files(paths, "NAME_DESC")
    assert __to_names(res6) == ["f", "e31", "d22", "c", "b14", "a43"]


def __to_names(paths: Iterable[Path]) -> List[str]:
    return list(map(lambda p: p.name, paths))
