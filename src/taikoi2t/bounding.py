from typing import Tuple

# (left, top, right, bottom)
type Bounding = Tuple[int, int, int, int]


# returns (width, height)
def size_of(bounding: Bounding) -> Tuple[int, int]:
    return (abs(bounding[2] - bounding[0]), abs(bounding[3] - bounding[1]))
