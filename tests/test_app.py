from pathlib import Path

from taikoi2t.app import empty_tsv_line
from taikoi2t.args import Args


def test_empty_tsv_line() -> None:
    settings1 = Args(dictionary=Path("dict"), opponent=True, verbose=0, files=[])
    res1 = empty_tsv_line(settings1)
    assert res1 == '""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""'

    settings2 = Args(dictionary=Path("dict"), opponent=False, verbose=0, files=[])
    res2 = empty_tsv_line(settings2)
    assert res2 == '""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""'
