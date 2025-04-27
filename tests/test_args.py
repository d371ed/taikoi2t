import sys

import pytest

from taikoi2t.args import parse_args


def test_parse_args_dictionary() -> None:
    res1 = parse_args("app -d dict1.csv image0.png".split())
    assert res1.dictionary.as_posix() == "dict1.csv"

    res2 = parse_args("app --dictionary dict2.csv image0.png".split())
    assert res2.dictionary.as_posix() == "dict2.csv"

    with pytest.raises(SystemExit) as e:
        parse_args("app dict3.csv image0.png".split())
    assert e.value.code == 2


def test_parse_args_opponent() -> None:
    # res1 = parse_args("app -d dict.csv --opponent image0.png".split())
    # assert res1.opponent is True

    # res2 = parse_args("app -d dict.csv image0.png".split())
    # assert res2.opponent is False

    # argparse.ArgumentParser maybe have internal states
    # store_true typed arguments cannot be tested
    pass


def test_parse_args_verbose() -> None:
    # res1 = parse_args("app -d dict.csv --verbose image0.png".split())
    # assert res1.verbose == 1

    # res2 = parse_args("app -d dict.csv image0.png".split())
    # assert res2.verbose == 0

    # argparse.ArgumentParser maybe have internal states
    # count typed arguments cannot be tested
    pass


def test_validate_args() -> None:
    pass  # TODO


def set_argv(command: str) -> None:
    reset_argv()
    sys.argv = command.split()


def reset_argv() -> None:
    del sys.argv[:]
