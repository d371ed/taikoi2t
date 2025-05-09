import json
from pathlib import Path
from typing import List, Tuple

import pytest

from taikoi2t.app import run


def test_run(capsys: pytest.CaptureFixture[str]) -> None:
    if not Path("./tests/images").exists():
        return  # skip

    targets: List[Tuple[str, str]] = [
        # sample screenshots are not contained in this repository
        # use this section if you want to test your screenshots
        (
            "app -d ./students.csv ./tests/images/0000.jpg",
            "TRUE\tホシノ\t臨ホシノ\tシロコ＊\tノノミ\t水シロコ\t水アヤネ\t水ハナコ\tミヤコ\tシロコ＊\tホシノ\t水シロコ\tヒビキ\n",
        ),
        (
            "app -d ./students.csv --csv ./tests/images/0007.png ./tests/images/0008.png",
            "FALSE,モモイ,ホシノ,ミドリ,エイミ,水シロコ,リオ,ホシノ,ミヤコ,シロコ＊,イオリ,水シロコ,ナギサ\n"
            + "TRUE,ホシノ,ハルナ,シロコ＊,アジュリ,水シロコ,サツキ,ホシノ,バネル,シュン,シロコ＊,水シロコ,カリン\n",
        ),
        (
            "app -d ./students.csv ./tests/images/0009.png ./README.md ./tests/images/0010.png",
            "TRUE\tホシノ\tバネル\tマリナ\tアジュリ\t水シロコ\tヒビキ\t水ハナコ\tマリナ\tシロコ＊\tホシノ\t水シロコ\tヒビキ\n"
            + "FALSE\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\tError\n"
            + "TRUE\tシロコ＊\tシュン\tホシノ\tレイサ\t水シロコ\tサツキ\tホシノ\tレイサ\tミドリ\tシロコ＊\t水シロコ\tヒビキ\n",
        ),
        (
            "app -d ./students.csv --opponent ./tests/images/0009.png",
            "TRUE\tホシノ\tバネル\tマリナ\tアジュリ\t水シロコ\tヒビキ\tError\t水ハナコ\tマリナ\tシロコ＊\tホシノ\t水シロコ\tヒビキ\n",
        ),
    ]
    for command, expected in targets:
        run(command.split())
        captured = capsys.readouterr()
        assert captured.out == expected
        assert captured.err == ""


def test_run_json(capsys: pytest.CaptureFixture[str]) -> None:
    if not Path("./tests/images").exists():
        return  # skip

    run("app -d ./students.csv --json ./tests/images/0000.jpg".split())
    captured = capsys.readouterr()
    out_json = json.loads(captured.out)
    assert out_json["matches"][0]["player"]["wins"] is True
    assert out_json["matches"][0]["player"]["strikers"]["striker1"]["name"] == "ホシノ"
    assert out_json["matches"][0]["opponent"]["owner"] != "null"
    assert captured.err == ""


def test_extract_match_result() -> None:
    pass  # TODO


def test_extract_student_names() -> None:
    pass  # TODO
