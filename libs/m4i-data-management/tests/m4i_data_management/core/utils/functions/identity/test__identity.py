from m4i_data_management.core.utils.functions.identity.identity import identity


def test__identity_string():
    assert identity("Hello world!") == "Hello world!"


# END test__identity_string


def test__identity_object():
    obj = {"test": "Hello world!"}
    assert identity(obj) == obj


# END test__identity_object
