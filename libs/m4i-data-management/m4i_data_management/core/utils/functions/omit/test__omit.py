from .omit import omit


def test__omit_does_not_modify_input():
    obj = {"test": "Hello world!", "abc": "def"}

    omit(obj, "test", "abc")

    assert "test" in obj
    assert "abc" in obj
# END test__omit_does_not_modify_input


def test__omit_multiple_keys():
    obj = {"test": "Hello world!", "abc": "def"}

    test = omit(obj, "test", "abc")

    assert "test" not in test
    assert "abc" not in test
# END test__omit_multiple_keys


def test__omit_none():
    obj = {"test": "Hello world!", "abc": "def"}

    test = omit(obj)

    assert "test" in test
    assert "abc" in test
# END test__omit_none


def test__omit_single_key():
    obj = {"test": "Hello world!", "abc": "def"}

    test = omit(obj, "test")

    assert "test" not in test
    assert "abc" in test
# END test__omit_single_key
