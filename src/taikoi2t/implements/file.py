import glob
from dataclasses import dataclass
from itertools import filterfalse
from pathlib import Path
from typing import Callable, Iterable, List

from taikoi2t.models.file import FileSortKeyOrder


def expand_paths(paths: Iterable[Path]) -> List[Path]:
    expanded: List[Path] = []
    for path in paths:
        path_str = path.as_posix()
        if "*" in path_str:  # wildcard
            expanded.extend(map(Path, sorted(glob.glob(path_str))))
        else:
            expanded.append(path)
    return expanded


def sort_files(paths: Iterable[Path], order_by: FileSortKeyOrder) -> List[Path]:
    sort_key = __SORT_KEYS[order_by]
    sortables = (
        list(filter(lambda p: p.exists(), paths)) if sort_key.needs_stat else paths
    )
    un_sortables = (
        list(filterfalse(lambda p: p.exists(), paths)) if sort_key.needs_stat else []
    )
    return (
        sorted(sortables, key=sort_key.selector, reverse=sort_key.reverse)
        + un_sortables
    )


@dataclass(frozen=True)
class __SortKey:
    key_order: FileSortKeyOrder
    selector: Callable[[Path], int | str]
    reverse: bool
    needs_stat: bool


__SORT_KEYS = dict(
    (s.key_order, s)
    for s in [
        __SortKey(
            "MODIFY_ASC", lambda p: p.stat().st_mtime_ns, reverse=False, needs_stat=True
        ),
        __SortKey(
            "MODIFY_DESC", lambda p: p.stat().st_mtime_ns, reverse=True, needs_stat=True
        ),
        __SortKey(
            "BIRTH_ASC",
            lambda p: p.stat().st_birthtime_ns,
            reverse=False,
            needs_stat=True,
        ),
        __SortKey(
            "BIRTH_DESC",
            lambda p: p.stat().st_birthtime_ns,
            reverse=True,
            needs_stat=True,
        ),
        __SortKey("NAME_ASC", lambda p: p.name, reverse=False, needs_stat=False),
        __SortKey("NAME_DESC", lambda p: p.name, reverse=True, needs_stat=False),
    ]
)
