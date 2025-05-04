from dataclasses import dataclass
from typing import Literal

from taikoi2t.args import Args

type OutputFormat = Literal["tsv", "csv", "json"]


@dataclass
class Settings:
    opponent: bool
    output_format: OutputFormat
    alias: bool
    sp_sort: bool
    verbose: int


def new_settings_from(args: Args) -> Settings:
    output_format: OutputFormat = "tsv"
    if args.csv:
        output_format = "csv"
    if args.json:
        output_format = "json"  # overwrite csv

    return Settings(
        opponent=args.opponent,
        output_format=output_format,
        alias=not args.no_alias,
        sp_sort=not args.no_sp_sort,
        verbose=args.verbose,
    )
