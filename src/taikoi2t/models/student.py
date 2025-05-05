from dataclasses import dataclass
from typing import Optional

DEFAULT_STUDENT_INDEX = -1
ERROR_STUDENT_NAME: str = "Error"


@dataclass(frozen=True)
class Student:
    index: int
    name: str
    alias: Optional[str]
