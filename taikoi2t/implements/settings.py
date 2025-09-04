from typing import Iterable

from taikoi2t.application.column import (
    COLUMN_DICTIONARY,
    DEFAULT_COLUMN_KEYS,
    OPPONENT_COLUMN_KEYS,
)
from taikoi2t.models.args import Args
from taikoi2t.models.settings import OutputFormat, Settings


def new_settings_from(args: Args) -> Settings:
    output_format: OutputFormat = "tsv"
    if args.csv:
        output_format = "csv"
    if args.json:
        output_format = "json"  # overwrite csv

    column_keys: Iterable[str]
    if output_format == "json":
        column_keys = []
    elif len(args.columns) > 0:
        column_keys = args.columns
    elif args.opponent:
        column_keys = OPPONENT_COLUMN_KEYS
    else:
        column_keys = DEFAULT_COLUMN_KEYS

    return Settings(
        columns=[
            COLUMN_DICTIONARY[key]
            for key in column_keys
            if key in COLUMN_DICTIONARY.keys()
        ],
        output_format=output_format,
        alias=not args.no_alias,
        sp_sort=not args.no_sp_sort,
        verbose=args.verbose,
    )
