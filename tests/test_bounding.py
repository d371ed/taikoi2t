from taikoi2t.bounding import Bounding, size_of


def test_size_of() -> None:
    bounding1: Bounding = (200, 300, 640, 420)
    assert size_of(bounding1) == (440, 120)

    bounding2: Bounding = (-100, 0, 0, 20)
    assert size_of(bounding2) == (100, 20)

    bounding3: Bounding = (10, 10, 0, -20)
    assert size_of(bounding3) == (10, 30)
