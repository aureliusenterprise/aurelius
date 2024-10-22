from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..exceptions import QualifiedNameNotValidException

from m4i_atlas_core import ConfigStore

store = ConfigStore.get_instance()


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BaseObject(DataClassJsonMixin):

    qualified_name: str

    def __post_init__(self):
        if store.get("validate_qualified_name", default=True):
            self.validate_qualified_name()
    # END __post_init__

    def validate_qualified_name(self):
        """
        Validates the current qualified name value. 
        If the value is not valid, raises a `QualifiedNameNotValidException`.
        """

        expected = self._qualified_name()

        if not self.qualified_name == expected:
            raise QualifiedNameNotValidException(
                f"Qualified name validation failed. Expected {expected} but received {self.qualified_name}."
            )
        # END IF
    # END validate_qualified_name

    def _qualified_name(self) -> str:
        """
        Returns the qualified name of the object based on some other properties of the object. 
        This qualified name is used as a reference by the `validate_qualified_name` method.
        Should be implemented by inheriting classes.
        """
        return self.qualified_name
    # END _qualified_name
# END BaseObject
