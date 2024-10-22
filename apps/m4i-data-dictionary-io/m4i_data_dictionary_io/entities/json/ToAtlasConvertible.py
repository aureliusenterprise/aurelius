from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from dataclasses_json import DataClassJsonMixin
from m4i_atlas_core import Entity

T = TypeVar('T', bound=Entity, covariant=True)


class ToAtlasConvertible(Generic[T], DataClassJsonMixin, ABC):
    """
    Entities that implement the `ToAtlasConvertible` protocol can be converted to a corresponding Atlas Entity by calling the `convert_to_atlas` function
    """

    @abstractmethod
    def convert_to_atlas(self) -> T:
        """
        Returns a corresponding Atlas Entity
        """
    # END convert_to_atlas

# END ToAtlasConvertible
