import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import List

from taikoi2t.implements.image import new_image_meta
from taikoi2t.implements.settings import Settings
from taikoi2t.implements.team import new_error_team
from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student


def get_match_id(time_ns: int, filename: str) -> str:
    sanitized_name = "".join(__unicode_to_hex(c) for c in filename if c.isalnum())
    return f"{time_ns}-{sanitized_name}"


def __unicode_to_hex(c: str) -> str:
    return c if c.isascii() else f"{ord(c):X}"


def render_match(match_result: MatchResult, settings: Settings) -> str:
    if settings.output_format == "json":
        return json.dumps(asdict(match_result), ensure_ascii=False)

    if len(settings.columns) == 0:
        return ""  # does not reach here in actual runs

    row: List[str] = []
    for column in settings.columns:
        for selected in column.selector(match_result):
            if isinstance(selected, Student):
                row.append(
                    selected.alias or selected.name if settings.alias else selected.name
                )
            else:
                row.append(selected)

    return ("," if settings.output_format == "csv" else "\t").join(row)


def new_errored_match_result(path: Path) -> MatchResult:
    return MatchResult(
        get_match_id(time.time_ns(), path.name),
        new_image_meta(path),
        new_error_team(),
        new_error_team(),
    )
