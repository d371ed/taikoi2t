from itertools import chain

from taikoi2t.application.column import COLUMN_DICTIONARY, COLUMNS


def test_COLUMN_DICTIONARY_key_duplication() -> None:
    source_keys = list(chain.from_iterable(column.keys for column in COLUMNS))
    assert len(source_keys) == len(COLUMN_DICTIONARY.keys())
