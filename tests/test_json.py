from dataclasses import dataclass

from taikoi2t.implements.json import to_json_str
from taikoi2t.models.json import CustomJSONSerializable, JSONType


@dataclass(frozen=True)
class _Address(CustomJSONSerializable):
    town: str
    number: int

    def to_json(self) -> JSONType:
        return f"{self.town}-{self.number}"


@dataclass(frozen=True)
class _Job:
    name: str
    pay: int

    # should be ignored
    def to_json(self) -> str:
        return f"{self.name}:{self.pay}"


@dataclass(frozen=True)
class _Person:
    id: int
    name: str
    address: _Address | None
    job: _Job | None


def test_to_json_str() -> None:
    person1 = _Person(1, "pn1", _Address("t1", 23), _Job("jn1", 4567))
    person2 = _Person(8, "pn2", None, None)

    actual1 = to_json_str([person1, person2])
    assert actual1 is not None
    expected1 = r'[{"id": 1, "name": "pn1", "address": "t1-23", "job": {"name": "jn1", "pay": 4567}}, {"id": 8, "name": "pn2", "address": null, "job": null}]'
    assert actual1.replace(" ", "") == expected1.replace(" ", "")

    actual2 = to_json_str([])
    assert actual2 is not None
    assert actual2 == "[]"

    actual3 = to_json_str(lambda: 42)
    assert actual3 is None
