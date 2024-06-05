from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from .ElasticIndexTemplateMappings import ElasticIndexTemplateMappings


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateModelBase(DataClassJsonMixin):
    mappings: ElasticIndexTemplateMappings


# END ElasticIndexTemplateModelBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateModelDefaultsBase(DataClassJsonMixin):
    pass


# END ElasticIndexTemplateModelDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateModel(
    ElasticIndexTemplateModelDefaultsBase,
    ElasticIndexTemplateModelBase,
):
    pass
# END ElasticIndexTemplateModel
