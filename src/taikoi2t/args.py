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


def parse_args() -> type[Args]:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-d", "--dictionary", type=Path, required=True, help="student dictionary (CSV)"
    )
    arg_parser.add_argument(
        "--opponent", action="store_true", help="include the name of opponent"
    )
    arg_parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=VERBOSE_SILENT,
        help="print messages and show images for debug (0: silent, 1: error, 2: print, 3: image)",
    )
    arg_parser.add_argument("files", type=Path, nargs="+")

    args = arg_parser.parse_args(args=None, namespace=Args)

    if not args.dictionary.exists():
        print(f"{args.dictionary.as_posix()} is not found", file=sys.stderr)
        sys.exit(1)

    if args.dictionary.suffix != ".csv":
        print(
            f"{args.dictionary.as_posix()} has invalid suffix as CSV", file=sys.stderr
        )
        sys.exit(1)

    return args
