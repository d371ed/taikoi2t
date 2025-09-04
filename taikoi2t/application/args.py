import argparse
import logging
from pathlib import Path
from typing import Sequence

from taikoi2t import TAIKOI2T_VERSION
from taikoi2t.application.column import COLUMN_DICTIONARY
from taikoi2t.models.args import VERBOSE_SILENT, Args
from taikoi2t.models.file import ALL_FILE_SORT_KEY_ORDERS

logger: logging.Logger = logging.getLogger("taikoi2t.args")


def parse_args(args: Sequence[str]) -> Args:
    arg_parser = argparse.ArgumentParser(args[0] if len(args) > 0 else None)
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
        "--file-sort",
        type=str,
        choices=sorted(ALL_FILE_SORT_KEY_ORDERS),
        default=None,
        help="sort input files (default: disabled)",
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=VERBOSE_SILENT,
        help="print messages and show images for debug (default: silent, -v: error, -vv: print, -vvv: image)",
    )
    arg_parser.add_argument(
        "--logfile",
        type=Path,
        default=None,
        help="output logs to this path (default: disabled)",
    )
    arg_parser.add_argument("files", type=Path, nargs="+", help="target images")

    namespace = Args(Path(), False, [], False, False, False, False, None, 0, None, [])
    return arg_parser.parse_args(args=args[1:], namespace=namespace)


# Returns False if there are critical errors
def validate_args(args: Args) -> bool:
    if not args.dictionary.exists():
        logger.critical(f"Dictionary file {args.dictionary.as_posix()} is not found")
        return False

    if args.dictionary.suffix != ".csv":
        logger.warning(f"{args.dictionary.as_posix()} has invalid suffix as CSV")

    unknown_columns: Sequence[str] = [
        c for c in args.columns if c not in COLUMN_DICTIONARY.keys()
    ]
    if len(unknown_columns) > 0:
        logger.critical(f"Unknown columns {', '.join(unknown_columns)}")
        return False

    return True
