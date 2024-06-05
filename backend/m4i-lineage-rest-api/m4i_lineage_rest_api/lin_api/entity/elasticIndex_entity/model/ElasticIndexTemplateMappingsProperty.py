from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from typing import Optional, Dict


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateMappingsPropertyBase(DataClassJsonMixin):
    pass


# END ElasticIndexTemplateMappingsPropertyBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateMappingsPropertyDefaultsBase(DataClassJsonMixin):
    format: Optional[str] = None
    properties: Dict[str, 'ElasticIndexTemplateMappingsProperty'] = field(default_factory=dict)
    type: Optional[str] = None


# END ElasticIndexTemplateMappingsPropertyDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateMappingsProperty(
    ElasticIndexTemplateMappingsPropertyDefaultsBase,
    ElasticIndexTemplateMappingsPropertyBase,
):
    pass
# END ElasticIndexTemplateMappingsProperty
