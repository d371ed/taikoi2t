from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from taikoi2t.models.json import CustomJSONSerializable, JSONType

DEFAULT_STUDENT_INDEX = -1
ERROR_STUDENT_NAME: str = "Error"


@dataclass(frozen=True)
class Student(CustomJSONSerializable):
    index: int
    name: str
    alias: Optional[str]

    @property
    def display_name(self) -> str:
        return self.alias or self.name

    @property
    def is_error(self) -> bool:
        return self.name == ERROR_STUDENT_NAME

    def to_json(self) -> JSONType:
        json = {key: getattr(self, key) for key in self.__annotations__}
        json["display_name"] = self.display_name
        return json


class StudentDictionary(ABC):
    @abstractmethod
    def validate(self) -> bool: ...
    @abstractmethod
    def get_allow_char_list(self) -> str: ...
    @abstractmethod
    def match(self, recognized_text: str) -> Student: ...
