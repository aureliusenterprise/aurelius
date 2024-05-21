from dataclasses import dataclass, field, fields
from typing import Optional

from dataclasses_json import (DataClassJsonMixin, LetterCase, config,
                              dataclass_json)
from m4i_atlas_core.entities.atlas.core.utils.create_placeholder_guid import \
    create_placehoder_guid

from ..attributes import Attributes


class ObjectIdHasNoReferenceException(Exception):
    """
    This exception is raised whenever an `ObjectId` is declared without a `guid` and without any `unique_attributes`
    """
# END ObjectIdHasNoReferenceException


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ObjectIdBase(DataClassJsonMixin):

    type_name: str

# END ObjectIdBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ObjectIdDefaultsBase(DataClassJsonMixin):

    guid: Optional[str] = field(default=None, metadata=config(
        exclude=lambda guid: guid is None
    ))
    unique_attributes: Optional[Attributes] = field(default_factory=dict)

# END ObjectIdDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ObjectId(ObjectIdDefaultsBase, ObjectIdBase):

    def __post_init__(self):
        self.validate_reference()
    # END __post_init__

    def validate_reference(self):
        """
        Validates whether or not a `guid` or at least one `unique_attribute` is specified
        """

        # Checks whether or not there are any unmapped unique attributes
        has_unmapped_unique_attribute = any(
            self.unique_attributes.unmapped_attributes.values()
        )

        # Checks whether there are any unique attributes mapped to class attributes
        # This can occur e.g. when an inheriting dataclass explicitly declares an attribute
        has_mapped_unique_attribute = any(
            getattr(self.unique_attributes, field.name)
            for field in fields(self.unique_attributes)
            if field.name != "attributes"
        )

        has_unique_attribute = has_unmapped_unique_attribute or has_mapped_unique_attribute

        if self.guid is None and not has_unique_attribute:
            raise ObjectIdHasNoReferenceException(
                "An ObjectId must specify a guid or at least one unique attribute"
            )
        # END IF
    # END validate_reference
# END ObjectId
