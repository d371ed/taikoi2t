from pathlib import Path

from taikoi2t.app import error_line
from taikoi2t.args import Args


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
