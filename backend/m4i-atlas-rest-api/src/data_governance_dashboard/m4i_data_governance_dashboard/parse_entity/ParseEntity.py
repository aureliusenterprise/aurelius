from dataclasses import dataclass
from typing import Dict, Union

from m4i_atlas_core import Entity
from dataclasses_json.api import LetterCase, dataclass_json

from ..core.domains import Domains


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ParseEntity:
    entity: Entity

    @property
    def get_dd_initials(self) -> Union[str, None]:
        """
        Get initials for the program
        :return: str | None
        """

        for program in list(Domains.__members__):
            if Domains[program].value == self._get_name:
                return str(program)

    def get_source(self) -> bool:
        """
        Boolean [True|False] if entity loaded by correct source
        :return: bool
        """

        if 'source' in self.entity.relationship_attributes:
            total_sources = len(self.entity.relationship_attributes['source'])
            sources = []
            for i in range(0, total_sources):
                sources.append(self.entity.relationship_attributes['source'][i]['displayText'])

            for program in list(Domains.__members__):

                # Check if path variable is from the list of Domains
                found = True if len([program for s in sources if program in s.split('/')]) > 0 else False
                if found:
                    if Domains[program].value == self._get_name:
                        return True
        # default
        return False

    # END get_source

    @property
    def _get_total_entities(self) -> int:
        """
        Total number of data entities for this `object`
        :return: int
        """

        if 'dataEntity' in self.entity.relationship_attributes:
            return len(self.entity.relationship_attributes['dataEntity'])
        else:
            return 0

    # END _get_total_entities

    @property
    def _get_name(self) -> str:
        """
        Get name for the Data Domain Entity
        :return: str
        """
        try:
            if hasattr(self.entity.attributes, 'name'):
                return getattr(self.entity.attributes, 'name')
            raise AttributeError
        except AttributeError:
            if 'name' in self.entity.attributes.unmapped_attributes:
                return self.entity.attributes.unmapped_attributes['name']
            raise KeyError
        except KeyError:
            return 'no_name'

    # END _get_name

    @property
    def _get_guid(self) -> str:
        """
        Return `GUID` for this `object`
        :return:
        """
        return self.entity.guid

    # END _get_guid

    def convert_to_details(self) -> Dict:
        """
        Creates internal structure for each program
        :return: dict
        """

        details = {
            "name": self._get_name,
            "guid": self._get_guid,
            "isActive": self.get_source(),
            "totalNumberOfEntities": self._get_total_entities
        }
        # print(details)

        return {
            self.get_dd_initials: details
        }

    # END convert_to_details
