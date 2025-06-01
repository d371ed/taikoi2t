import csv
import glob
import logging
from pathlib import Path
from typing import Iterable, List, Tuple

logger: logging.Logger = logging.getLogger("taikoi2t.file")


def read_student_dictionary_source_file(path: Path) -> List[Tuple[str, str]] | None:
    if not path.exists():
        logger.critical(f"{path.as_posix()} is not found")
        return None
    if not path.is_file():
        logger.critical(f"{path.as_posix()} is not file")
        return None

    rows: List[Tuple[str, str]] = []
    try:
        with path.open(mode="r", encoding="utf-8") as students_file:
            for index, row in enumerate(csv.reader(students_file)):
                if len(row) == 0:
                    logger.warning(f"Empty line at line {index + 1}")
                elif len(row[0]) == 0:
                    logger.warning(f"Empty name at line {index + 1}; {row}")
                else:
                    rows.append((row[0], row[1] if len(row) >= 2 else ""))
    except UnicodeDecodeError:
        logger.critical(f"{path.as_posix()} is invalid as an UTF-8 text")
        return None

    if len(rows) == 0:
        logger.critical(f"{path.as_posix()} is invalid as student's dictionary")
        return None
    return rows


def expand_paths(paths: Iterable[Path]) -> List[Path]:
    expanded: List[Path] = []
    for path in paths:
        path_str = path.as_posix()
        if "*" in path_str:  # wildcard
            expanded.extend(map(Path, sorted(glob.glob(path_str))))
        else:
            expanded.append(path)
    return expanded
