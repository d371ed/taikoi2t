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


@dataclass
class ImageMeta:
    path: str
    name: str
    width: Optional[int] = None
    height: Optional[int] = None
    modal: Optional[BoundingBox] = None
