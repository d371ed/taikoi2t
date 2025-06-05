from pathlib import Path

import numpy

from taikoi2t.implements.image import crop, new_image_meta
from taikoi2t.models.image import BoundingBox, Image


def test_crop() -> None:
    image1: Image = numpy.zeros((100, 200, 3), dtype=numpy.uint8)
    res1 = crop(image1, BoundingBox(10, 0, 50, 80))
    assert res1.shape == (80, 40, 3)

    res2 = crop(image1, BoundingBox(-10, 0, 50, 180))
    assert res2.shape == (100, 50, 3)

    res3 = crop(image1, BoundingBox(120, 50, 20, 30))
    assert res3.shape == (20, 100, 3)


def test_new_image_meta(tmp_path: Path) -> None:
    path1 = tmp_path / "image0.png"
    path1.touch()

    res1 = new_image_meta(path1, (1000, 2000), BoundingBox(33, 44, 55, 66))
    assert "image0.png" in res1.path
    assert res1.name == "image0.png"
    assert len(res1.path) > len(res1.name)
    assert res1.birth_time_ns is not None
    assert res1.modify_time_ns is not None
    assert res1.width == 1000
    assert res1.height == 2000
    assert res1.modal == BoundingBox(33, 44, 55, 66)

    res2 = new_image_meta(tmp_path / "not_found.png")
    assert res2.birth_time_ns is None
    assert res2.modify_time_ns is None
    assert res2.width is None
    assert res2.height is None
    assert res2.modal is None
