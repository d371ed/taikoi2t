from taikoi2t.main import check, load_image


def test_nothing():
    assert True


def test_check():
    assert check()


def test_load_image():
    assert load_image("tests/images/0000.jpg")


# def test_image_to_text():
#     assert image_to_text("tests/images/0007.png") == "hoge"
