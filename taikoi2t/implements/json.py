import json
import logging
from dataclasses import is_dataclass
from typing import Any

from taikoi2t.models.json import CustomJSONSerializable, JSONType

logger: logging.Logger = logging.getLogger("taikoi2t.json")


def to_json_str(obj: Any) -> str | None:
    try:
        return json.dumps(
            obj, default=__custom_json_serializable_default, ensure_ascii=False
        )
    except TypeError as e:
        logger.error(e)
        return None


def __custom_json_serializable_default(obj: Any) -> JSONType:
    if isinstance(obj, CustomJSONSerializable):
        return obj.to_json()
    elif is_dataclass(obj):
        return {key: getattr(obj, key) for (key, _) in obj.__dataclass_fields__.items()}
    raise TypeError(f"Unsupported type: {type(obj).__name__}; value: {obj}")
