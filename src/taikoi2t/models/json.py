from abc import ABC, abstractmethod
from typing import Dict, List

type JSONType = (
    Dict[str, "JSONType"] | List["JSONType"] | str | int | float | bool | None
)


class CustomJSONSerializable(ABC):
    @abstractmethod
    def to_json(self) -> JSONType: ...
