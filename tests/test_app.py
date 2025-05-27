import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

import cv2
import easyocr  # type: ignore
import pytest

from taikoi2t.app import run
from taikoi2t.application.file import read_student_dictionary_source_file
from taikoi2t.application.match import extract_match_result
from taikoi2t.application.student import StudentDictionary
from taikoi2t.models.args import VERBOSE_SILENT
from taikoi2t.models.image import Image, ImageMeta
from taikoi2t.models.match import MatchResult
from taikoi2t.models.settings import Settings


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
    # the format of expected_results.csv is the same as the following command
    # poetry run -- taikoi2t -d .\students.csv --csv --no-alias -c IMAGE_PATH PWIN PNAME PTEAM OWIN ONAME OTEAM --
    expected_results_path = Path("./tests/images/expected_results.csv")
    if not expected_results_path.exists():
        return  # skip

    dictionary = StudentDictionary(
        read_student_dictionary_source_file(Path("./students.csv")) or []
    )
    reader = easyocr.Reader(["ja", "en"])
    settings = Settings(
        columns=[],
        output_format="json",
        alias=True,
        sp_sort=True,
        verbose=VERBOSE_SILENT,
    )

    with expected_results_path.open(
        mode="r", encoding="utf-8"
    ) as expected_results_file:
        for row in csv.reader(expected_results_file):
            expected_result = new_expected_result_from(row)
            image_meta = ImageMeta(
                expected_result.path.as_posix(), expected_result.path.name
            )
            source_image: Image = cv2.imread(image_meta.path)

            actual = extract_match_result(
                source_image, image_meta, dictionary, reader, settings
            )
            assert actual is not None

            expected_result.assert_match(actual)


@dataclass(frozen=True)
class ExpectedResult:
    path: Path
    player_wins: bool
    player_name: str
    p1: str
    p2: str
    p3: str
    p4: str
    p5: str
    p6: str
    opponent_wins: bool
    opponent_name: str
    o1: str
    o2: str
    o3: str
    o4: str
    o5: str
    o6: str

    def assert_match(self, match: MatchResult) -> None:
        assert match.player.wins is self.player_wins
        assert (match.player.owner is not None) is (self.player_name != "Error")
        assert match.player.strikers.striker1.name == self.p1
        assert match.player.strikers.striker2.name == self.p2
        assert match.player.strikers.striker3.name == self.p3
        assert match.player.strikers.striker4.name == self.p4
        assert match.player.specials.special1.name == self.p5
        assert match.player.specials.special2.name == self.p6

        assert match.opponent.wins is self.opponent_wins
        assert (match.opponent.owner is not None) is (self.opponent_name != "Error")
        assert match.opponent.strikers.striker1.name == self.o1
        assert match.opponent.strikers.striker2.name == self.o2
        assert match.opponent.strikers.striker3.name == self.o3
        assert match.opponent.strikers.striker4.name == self.o4
        assert match.opponent.specials.special1.name == self.o5
        assert match.opponent.specials.special2.name == self.o6


def new_expected_result_from(row: Sequence[str]) -> ExpectedResult:
    return ExpectedResult(
        path=Path(row[0]),
        player_wins=row[1] == "TRUE",
        player_name=row[2],
        p1=row[3],
        p2=row[4],
        p3=row[5],
        p4=row[6],
        p5=row[7],
        p6=row[8],
        opponent_wins=row[9] == "TRUE",
        opponent_name=row[10],
        o1=row[11],
        o2=row[12],
        o3=row[13],
        o4=row[14],
        o5=row[15],
        o6=row[16],
    )
