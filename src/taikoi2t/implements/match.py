import json
from dataclasses import asdict
from typing import List

from taikoi2t.implements.settings import Settings
from taikoi2t.implements.team import new_error_team
from taikoi2t.models.image import ImageMeta
from taikoi2t.models.match import MatchResult
from taikoi2t.models.student import Student


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


def new_errored_match_result(image: ImageMeta) -> MatchResult:
    return MatchResult(image, new_error_team(), new_error_team())
