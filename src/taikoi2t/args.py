import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class Args:
    dictionary: Path
    opponent: bool
    verbose: bool
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
        "--verbose", action="store_true", help="print messages for debug"
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
