from taikoi2t.bounding import Bounding, size


def test_size() -> None:
    bounding1: Bounding = (200, 300, 640, 420)
    assert size(bounding1) == (440, 120)

    bounding2: Bounding = (-100, 0, 0, 20)
    assert size(bounding2) == (100, 20)

    bounding3: Bounding = (10, 10, 0, -20)
    assert size(bounding3) == (10, 30)
