import argparse
import sys
from pathlib import Path
from typing import List, Sequence

from taikoi2t import TAIKOI2T_VERSION
from taikoi2t.implements.column import COLUMN_DICTIONARY
from taikoi2t.models.args import VERBOSE_ERROR, VERBOSE_SILENT, Args


def parse_args(args: Sequence[str]) -> Args:
    if len(args) == 0:
        print("FATAL: args is empty", file=sys.stderr)
        sys.exit(1)

    arg_parser = argparse.ArgumentParser(args[0])
    arg_parser.add_argument(
        "--version", action="version", version=f"taikoi2t {TAIKOI2T_VERSION}"
    )

    arg_parser.add_argument(
        "-d", "--dictionary", type=Path, required=True, help="student dictionary (CSV)"
    )

    column_group = arg_parser.add_mutually_exclusive_group()
    column_group.add_argument(
        "--opponent", action="store_true", help="include the name of opponent"
    )
    column_group.add_argument(
        "-c", "--columns", nargs="+", help="select columns in a row"
    )

    format_group = arg_parser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--csv", action="store_true", help="change output to CSV (default: TSV)"
    )
    format_group.add_argument(
        "--json", action="store_true", help="change output to JSON (default: TSV)"
    )

    arg_parser.add_argument(
        "--no-alias",
        action="store_true",
        help="turn off alias mapping for student's name",
    )
    arg_parser.add_argument(
        "--no-sp-sort", action="store_true", help="turn off sorting specials"
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=VERBOSE_SILENT,
        help="print messages and show images for debug (default: silent, -v: error, -vv: print, -vvv: image)",
    )
    arg_parser.add_argument("files", type=Path, nargs="+", help="target images")

    namespace = Args(Path(), False, [], False, False, False, False, 0, [])
    return arg_parser.parse_args(args=args[1:], namespace=namespace)


def validate_args(args: Args) -> bool:
    if not args.dictionary.exists():
        print(
            f"FATAL: dictionary file {args.dictionary.as_posix()} is not found",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.dictionary.suffix != ".csv" and args.verbose >= VERBOSE_ERROR:
        print(
            f"WARNING: {args.dictionary.as_posix()} has invalid suffix as CSV",
            file=sys.stderr,
        )

    unknown_columns: List[str] = [
        c for c in args.columns if c not in COLUMN_DICTIONARY.keys()
    ]
    if len(unknown_columns) > 0:
        print(f"FATAL: unknown columns {', '.join(unknown_columns)}", file=sys.stderr)
        sys.exit(1)

    return True  # currently always returns True
