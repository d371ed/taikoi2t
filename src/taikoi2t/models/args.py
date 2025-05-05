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
    columns: Sequence[str]
    csv: bool
    json: bool
    no_alias: bool
    no_sp_sort: bool
    verbose: int
    files: Sequence[Path]
