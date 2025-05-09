import csv
from pathlib import Path
from typing import List, Tuple


def read_student_dictionary_source_file(path: Path) -> List[Tuple[str, str]] | None:
    rows: List[Tuple[str, str]]
    with path.open(mode="r", encoding="utf-8") as students_file:
        try:
            rows = [
                (row[0], row[1] if len(row) >= 2 else "")
                for row in csv.reader(students_file)
            ]
        except IndexError:
            return None
    if len(rows) == 0:
        return None
    return rows
