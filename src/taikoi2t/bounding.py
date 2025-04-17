from typing import Tuple

type Bounding = Tuple[int, int, int, int]


def size(bounding: Bounding) -> tuple[int, int]:
    return (bounding[2] - bounding[0], bounding[3] - bounding[1])
