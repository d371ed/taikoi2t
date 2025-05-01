from pathlib import Path
from typing import List, Tuple

import pytest

from taikoi2t.app import error_line, run
from taikoi2t.args import Args


def test_run(capsys: pytest.CaptureFixture[str]) -> None:
    targets: List[Tuple[str, str]] = [
        # sample screenshots are not contained in this repository
        # use this section if you want to test your screenshots
        # (
        #     "app -d ./students.csv ./tests/images/0000.jpg",
        #     "TRUE\tホシノ\t臨ホシノ\tシロコ＊\tノノミ\t水シロコ\t水アヤネ\t水ハナコ\tミヤコ\tシロコ＊\tホシノ\t水シロコ\tヒビキ\n",
        # ),
        # (
        #     "app -d ./students.csv --csv ./tests/images/0007.png ./tests/images/0008.png",
        #     "FALSE,モモイ,ホシノ,ミドリ,エイミ,水シロコ,リオ,ホシノ,ミヤコ,シロコ＊,イオリ,水シロコ,ナギサ\n"
        #     + "TRUE,ホシノ,ハルナ,シロコ＊,アジュリ,水シロコ,サツキ,ホシノ,バネル,シュン,シロコ＊,水シロコ,カリン\n",
        # ),
        # (
        #     "app -d ./students.csv ./tests/images/0009.png ./README.md ./tests/images/0010.png",
        #     "TRUE\tホシノ\tバネル\tマリナ\tアジュリ\t水シロコ\tヒビキ\t水ハナコ\tマリナ\tシロコ＊\tホシノ\t水シロコ\tヒビキ\n"
        #     + "FALSE\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\n"
        #     + "TRUE\tシロコ＊\tシュン\tホシノ\tレイサ\t水シロコ\tサツキ\tホシノ\tレイサ\tミドリ\tシロコ＊\t水シロコ\tヒビキ\n",
        # ),
    ]
    for command, expected in targets:
        run(command.split())
        captured = capsys.readouterr()
        assert captured.out == expected
        assert captured.err == ""


def test_empty_tsv_line() -> None:
    settings1 = Args(
        dictionary=Path("dict"), opponent=True, csv=False, verbose=0, files=[]
    )
    res1 = error_line(settings1)
    assert (
        res1
        == "FALSE\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError"
    )

    settings2 = Args(
        dictionary=Path("dict"), opponent=False, csv=False, verbose=0, files=[]
    )
    res2 = error_line(settings2)
    assert (
        res2
        == "FALSE\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError"
    )

    settings3 = Args(
        dictionary=Path("dict"), opponent=True, csv=True, verbose=0, files=[]
    )
    res3 = error_line(settings3)
    assert (
        res3
        == "FALSE,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error"
    )

    settings4 = Args(
        dictionary=Path("dict"), opponent=False, csv=True, verbose=0, files=[]
    )
    res4 = error_line(settings4)
    assert (
        res4
        == "FALSE,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error,Error"
    )
