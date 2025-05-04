from pathlib import Path

from taikoi2t.args import VERBOSE_SILENT, Args
from taikoi2t.settings import new_settings_from


def test_new_settings_from_output_format() -> None:
    res1 = new_settings_from(__new_args(csv=False, json=False))
    assert res1.output_format == "tsv"

    res2 = new_settings_from(__new_args(csv=True, json=False))
    assert res2.output_format == "csv"

    res3 = new_settings_from(__new_args(csv=False, json=True))
    assert res3.output_format == "json"

    res4 = new_settings_from(__new_args(csv=True, json=True))
    assert res4.output_format == "json"


def __new_args(csv: bool, json: bool) -> Args:
    return Args(
        dictionary=Path(),
        opponent=False,
        csv=csv,
        json=json,
        no_alias=False,
        no_sp_sort=False,
        verbose=VERBOSE_SILENT,
        files=[],
    )
