from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from taikoi2t.models.file import FileSortKeyOrder

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
    file_sort: Optional[FileSortKeyOrder]
    verbose: int
    logfile: Optional[Path]
    files: Sequence[Path]
