from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json
from m4i_atlas_core import Entity

from .validated_input import ValidatedInput


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class ValidatedInputWithPreviousEntity(ValidatedInput):
    """
    Represents a version of `ValidatedInput` that also includes the previous version of an entity.

    Attributes
    ----------
    previous_version : ElasticSearchEntity
        The previous version of the entity from Elasticsearch before any changes were made.
    """

    previous_version: Entity
