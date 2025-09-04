from typing import Literal, Set, TypeAlias, get_args

__FileSortKeyOrder: TypeAlias = Literal[
    "BIRTH_ASC", "BIRTH_DESC", "MODIFY_ASC", "MODIFY_DESC", "NAME_ASC", "NAME_DESC"
]
type FileSortKeyOrder = __FileSortKeyOrder
ALL_FILE_SORT_KEY_ORDERS: Set[FileSortKeyOrder] = set(get_args(__FileSortKeyOrder))
