from .identity import identity


def test__identity_string():
    assert identity("Hello world!") is "Hello world!"
# END test__identity_string


def test__identity_object():
    obj = {"test": "Hello world!"}
    assert identity(obj) is obj
# END test__identity_object
