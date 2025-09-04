from dataclasses import dataclass
from typing import Optional

import numpy

type Image = numpy.typing.NDArray[numpy.uint8]


@dataclass(frozen=True)
class BoundingBox:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return abs(self.right - self.left)

    @property
    def height(self) -> int:
        return abs(self.bottom - self.top)

    def is_empty(self) -> bool:
        return self.width == 0 or self.height == 0

    # convert numpy integers
    def as_python_int(self) -> "BoundingBox":
        return BoundingBox(
            int(self.left), int(self.top), int(self.right), int(self.bottom)
        )


@dataclass(frozen=True)
class RelativeBox:
    left: float
    top: float
    right: float
    bottom: float


@dataclass(frozen=True)
class ImageMeta:
    path: str
    name: str
    birth_time_ns: Optional[int]  # in nanoseconds
    modify_time_ns: Optional[int]
    width: Optional[int]
    height: Optional[int]
    modal: Optional[BoundingBox]
