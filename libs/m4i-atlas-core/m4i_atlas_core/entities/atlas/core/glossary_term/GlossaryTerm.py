from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..glossary_base_object import (GlossaryBaseObjectBase,
                                    GlossaryBaseObjectDefaultsBase)
from ..glossary_header import GlossaryHeader
from ..related_object_id import RelatedObjectId
from ..related_term_header import RelatedTermHeader
from ..term_categorization_header import TermCategorizationHeader


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryTermBase(GlossaryBaseObjectBase):

    anchor: GlossaryHeader

# END GlossaryTermBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryTermDefaultsBase(GlossaryBaseObjectDefaultsBase):

    abbreviation: Optional[str] = None
    antonyms: List[RelatedTermHeader] = field(default_factory=list)
    assigned_entities: List[RelatedObjectId] = field(default_factory=list)
    categories: List[TermCategorizationHeader] = field(default_factory=list)
    classifies: List[RelatedTermHeader] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    is_a: List[RelatedTermHeader] = field(default_factory=list)
    preferred_terms: List[RelatedTermHeader] = field(default_factory=list)
    preferred_to_terms: List[RelatedTermHeader] = field(default_factory=list)
    replaced_by: List[RelatedTermHeader] = field(default_factory=list)
    replacement_terms: List[RelatedTermHeader] = field(default_factory=list)
    see_also: List[RelatedTermHeader] = field(default_factory=list)
    translated_terms: List[RelatedTermHeader] = field(default_factory=list)
    translation_terms: List[RelatedTermHeader] = field(default_factory=list)
    usage: Optional[str] = None
    valid_values: List[RelatedTermHeader] = field(default_factory=list)
    valid_values_for: List[RelatedTermHeader] = field(default_factory=list)

# END GlossaryTermDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryTerm(GlossaryTermDefaultsBase, GlossaryTermBase):

    pass

# END GlossaryTerm
