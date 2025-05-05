from pathlib import Path
from typing import Sequence

from taikoi2t.implements.column import DEFAULT_COLUMN_KEYS, OPPONENT_COLUMN_KEYS
from taikoi2t.implements.settings import new_settings_from
from taikoi2t.models.args import VERBOSE_SILENT, Args
from taikoi2t.models.column import Column
from taikoi2t.models.settings import Settings


def test_requirements() -> None:
    def new_settings(columns: Sequence[Column]) -> Settings:
        return Settings(
            columns=columns,
            output_format="tsv",
            alias=True,
            sp_sort=True,
            verbose=VERBOSE_SILENT,
        )

    assert new_settings([]).requirements == set()
    assert new_settings(
        [Column(["AAA"], "students", lambda _: [])]
    ).requirements == set(["students"])
    assert new_settings(
        [
            Column(["AAA"], "students", lambda _: []),
            Column(["BBB", "B"], "win_or_lose", lambda _: []),
        ]
    ).requirements == set(["students", "win_or_lose"])
    assert new_settings(
        [
            Column(["CCC"], "opponent", lambda _: []),
            Column(["DDD", "D"], None, lambda _: []),
            Column(["EEE"], "win_or_lose", lambda _: []),
        ]
    ).requirements == set(["win_or_lose", "opponent"])


def test_new_settings_from_mapping_bools() -> None:
    res1 = new_settings_from(__new_args(opponent=True))
    assert (res1.output_format, res1.alias, res1.sp_sort) == ("tsv", True, True)

    res2 = new_settings_from(__new_args(csv=True))
    assert (res2.output_format, res2.alias, res2.sp_sort) == ("csv", True, True)

    res3 = new_settings_from(__new_args(json=True))
    assert (res3.output_format, res3.alias, res3.sp_sort) == ("json", True, True)

    res4 = new_settings_from(__new_args(no_alias=True))
    assert (res4.output_format, res4.alias, res4.sp_sort) == ("tsv", False, True)

    res5 = new_settings_from(__new_args(no_sp_sort=True))
    assert (res5.output_format, res5.alias, res5.sp_sort) == ("tsv", True, False)


def test_new_settings_from_output_format() -> None:
    res1 = new_settings_from(__new_args(csv=False, json=False))
    assert res1.output_format == "tsv"

    res2 = new_settings_from(__new_args(csv=True, json=False))
    assert res2.output_format == "csv"

    res3 = new_settings_from(__new_args(csv=False, json=True))
    assert res3.output_format == "json"

    res4 = new_settings_from(__new_args(csv=True, json=True))
    assert res4.output_format == "json"


def test_new_settings_from_columns() -> None:
    res1 = new_settings_from(__new_args(opponent=False, columns=[], json=False))
    for column, expected_key in zip(res1.columns, DEFAULT_COLUMN_KEYS):
        assert expected_key in column.keys

    res2 = new_settings_from(__new_args(opponent=True, columns=[], json=False))
    for column, expected_key in zip(res2.columns, OPPONENT_COLUMN_KEYS):
        assert expected_key in column.keys

    res3 = new_settings_from(__new_args(opponent=False, columns=[], json=True))
    assert res3.columns == []

    res4 = new_settings_from(
        __new_args(opponent=False, columns=["OTEAM", "OWIN"], json=False)
    )
    for column, expected_key in zip(res4.columns, ["OTEAM", "OWIN"]):
        assert expected_key in column.keys

    # json overrides all
    res5 = new_settings_from(__new_args(opponent=True, columns=["PWIN"], json=True))
    assert res5.columns == []

    # columns overrides opponent
    res6 = new_settings_from(__new_args(opponent=True, columns=["PWIN"], json=False))
    assert len(res6.columns) == 1
    assert "PWIN" in res6.columns[0].keys


def __new_args(
    opponent: bool = False,
    columns: Sequence[str] = [],
    csv: bool = False,
    json: bool = False,
    no_alias: bool = False,
    no_sp_sort: bool = False,
) -> Args:
    return Args(
        dictionary=Path(),
        opponent=opponent,
        columns=columns,
        csv=csv,
        json=json,
        no_alias=no_alias,
        no_sp_sort=no_sp_sort,
        verbose=VERBOSE_SILENT,
        files=[],
    )
