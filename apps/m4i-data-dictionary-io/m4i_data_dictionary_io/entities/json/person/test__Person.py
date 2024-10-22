from .Person import Person


def test__create_person_from_dict():
    """
    Tests whether or not a `Person` can be created from a dict with its attributes
    """

    person = {
        "email": "person@example.com",
        "name": "person",
        "source": "source"
    }

    instance = Person.from_dict(person)

    assert instance.email == "person@example.com"
    assert instance.name == "person"
    assert instance.source == "source"
# END test__create_person_from_dict


def test__create_person_from_json():
    """
    Tests whether or not a `Person` can be created from a json string with its attributes
    """

    person = (
        """
        {
            "email": "person@example.com",
            "name": "person",
            "source": "source"
        }
        """
    )

    instance = Person.from_json(person)

    assert instance.email == "person@example.com"
    assert instance.name == "person"
    assert instance.source == "source"
# END test__create_person_from_json


def test__person_convert_to_atlas_entity():
    """
    Tests whether or not all required fields are correctly converted to the atlas format.
    """

    person = {
        "email": "person@example.com",
        "name": "person",
        "source": "source"
    }

    instance = Person.from_dict(person)

    atlas_instance = instance.convert_to_atlas()

    atlas_attributes = atlas_instance.attributes

    assert atlas_attributes.name == instance.name
    assert atlas_attributes.email == instance.email
    assert atlas_attributes.qualified_name == instance.email

    atlas_source = atlas_attributes.source[0]

    assert atlas_source is not None
    assert atlas_source.type_name == "m4i_source"
    assert getattr(atlas_source.unique_attributes,
                   "qualified_name") == instance.source

# END test__person_convert_to_atlas_entity
