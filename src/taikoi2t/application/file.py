import csv
import logging
from pathlib import Path
from typing import List, Tuple

logger: logging.Logger = logging.getLogger("taikoi2t.file")


def read_student_dictionary_source_file(path: Path) -> List[Tuple[str, str]] | None:
    if not path.exists():
        logger.critical(f"{path.as_posix()} is not found")
        return None
    if not path.is_file():
        logger.critical(f"{path.as_posix()} is not a file")
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
