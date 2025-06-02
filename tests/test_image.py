from pathlib import Path

from taikoi2t.implements.image import new_image_meta
from taikoi2t.models.image import BoundingBox


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
