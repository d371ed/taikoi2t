from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

DEFAULT_STUDENT_INDEX = -1
ERROR_STUDENT_NAME: str = "Error"


@dataclass(frozen=True)
class Student:
    index: int
    name: str
    alias: Optional[str]

    @property
    def is_error(self) -> bool:
        return self.name == ERROR_STUDENT_NAME


class StudentDictionary(ABC):
    @abstractmethod
    def validate(self) -> bool: ...
    @abstractmethod
    def get_allow_char_list(self) -> str: ...
    @abstractmethod
    def match(self, recognized_text: str) -> Student: ...
