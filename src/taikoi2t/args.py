import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

VERBOSE_SILENT = 0
VERBOSE_ERROR = 1
VERBOSE_PRINT = 2
VERBOSE_IMAGE = 3


@dataclass
class Args:
    dictionary: Path
    opponent: bool
    verbose: int
    files: Sequence[Path]


def parse_args(args: Sequence[str]) -> Args:
    if len(args) == 0:
        print("FATAL: args is empty", file=sys.stderr)
        sys.exit(1)
    arg_parser = argparse.ArgumentParser(args[0])

    arg_parser.add_argument(
        "-d", "--dictionary", type=Path, required=True, help="student dictionary (CSV)"
    )
    arg_parser.add_argument(
        "--opponent", action="store_true", help="include the name of opponent"
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=VERBOSE_SILENT,
        help="print messages and show images for debug (default: silent, -v: error, -vv: print, -vvv: image)",
    )
    arg_parser.add_argument("files", type=Path, nargs="+", help="target images")

    return arg_parser.parse_args(args=args[1:], namespace=Args(Path(), False, 0, []))


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

    return True  # currently always returns True
