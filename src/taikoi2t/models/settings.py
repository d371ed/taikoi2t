from dataclasses import dataclass
from functools import cached_property
from typing import Literal, Sequence, Set

from taikoi2t.models.column import ALL_REQUIREMENTS, Column, Requirement

type OutputFormat = Literal["tsv", "csv", "json"]


@dataclass(frozen=True)
class Settings:
    columns: Sequence[Column]
    output_format: OutputFormat
    alias: bool
    sp_sort: bool
    verbose: int

    @cached_property
    def requirements(self) -> Set[Requirement]:
        if self.output_format == "json":
            return ALL_REQUIREMENTS
        else:
            return set(
                column.requirement
                for column in self.columns
                if column.requirement is not None
            )
