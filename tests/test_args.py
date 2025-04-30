from pathlib import Path

import pytest

from taikoi2t.args import (
    VERBOSE_ERROR,
    VERBOSE_IMAGE,
    VERBOSE_PRINT,
    VERBOSE_SILENT,
    Args,
    parse_args,
    validate_args,
)


def test_parse_args_dictionary() -> None:
    res1 = parse_args("app -d dict1.csv image0.png".split())
    assert res1.dictionary.as_posix() == "dict1.csv"

    res2 = parse_args("app --dictionary dict2.csv image0.png".split())
    assert res2.dictionary.as_posix() == "dict2.csv"

    with pytest.raises(SystemExit) as e:
        parse_args("app dict3.csv image0.png".split())
    assert e.value.code == 2


def test_parse_args_opponent() -> None:
    res1 = parse_args("app -d dict.csv --opponent image0.png".split())
    assert res1.opponent is True

    res2 = parse_args("app -d dict.csv image0.png".split())
    assert res2.opponent is False


def test_parse_args_verbose() -> None:
    res1 = parse_args("app -d dict.csv --verbose image0.png".split())
    assert res1.verbose == VERBOSE_ERROR

    res2 = parse_args("app -d dict.csv image0.png".split())
    assert res2.verbose == VERBOSE_SILENT

    res3 = parse_args("app -d dict.csv -v image0.png".split())
    assert res3.verbose == VERBOSE_ERROR

    res4 = parse_args("app -d dict.csv -vv image0.png".split())
    assert res4.verbose == VERBOSE_PRINT

    res5 = parse_args("app -d dict.csv -vvv image0.png".split())
    assert res5.verbose == VERBOSE_IMAGE


def test_parse_args_csv() -> None:
    res1 = parse_args("app -d dict.csv --csv image0.png".split())
    assert res1.csv is True

    res2 = parse_args("app -d dict.csv image0.png".split())
    assert res2.csv is False


def test_parse_args_files() -> None:
    res1 = parse_args("app -d dict.csv image0.png".split())
    assert [f.as_posix() for f in res1.files] == ["image0.png"]

    res2 = parse_args("app -d dict.csv image0.png image1.png".split())
    assert [f.as_posix() for f in res2.files] == ["image0.png", "image1.png"]

    with pytest.raises(SystemExit) as e:
        parse_args("app -d dict.csv".split())
    assert e.value.code == 2


def test_validate_args_valid(capsys: pytest.CaptureFixture[str]) -> None:
    args1 = Args(
        dictionary=Path("./students.csv"),
        opponent=False,
        csv=False,
        verbose=VERBOSE_SILENT,
        files=[Path("image0.png")],
    )
    assert validate_args(args1) is True

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_validate_args_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    args1 = Args(
        dictionary=Path("./404.csv"),
        opponent=False,
        csv=False,
        verbose=VERBOSE_SILENT,
        files=[Path("image0.png")],
    )
    with pytest.raises(SystemExit) as e:
        validate_args(args1)
    assert e.value.code == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "FATAL: dictionary file 404.csv is not found\n"


def test_validate_args_invalid_suffix_verbose_silent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    args1 = Args(
        dictionary=Path("./README.md"),
        opponent=False,
        csv=False,
        verbose=VERBOSE_SILENT,
        files=[Path("image0.png")],
    )
    assert validate_args(args1) is True

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_validate_args_invalid_suffix_verbose_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    args1 = Args(
        dictionary=Path("./README.md"),
        opponent=False,
        csv=False,
        verbose=VERBOSE_ERROR,
        files=[Path("image0.png")],
    )
    assert validate_args(args1) is True

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "WARNING: README.md has invalid suffix as CSV\n"
