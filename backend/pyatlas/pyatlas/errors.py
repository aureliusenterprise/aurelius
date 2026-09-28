"""Atlas compatible error codes and exception type.

The REST layer renders :class:`AtlasBaseException` exactly like Atlas does::

    {"errorCode": "ATLAS-404-00-005", "errorMessage": "Given instance guid x is invalid/not found"}
"""
from __future__ import annotations

from enum import Enum


class AtlasErrorCode(Enum):
    UNKNOWN_TYPENAME = (400, "ATLAS-400-00-00A", "{0}: Unknown/invalid typename")
    TYPE_MATCH_FAILED = (400, "ATLAS-400-00-010", "Given type {0} doesn't match {1}")
    INVALID_TYPE_DEFINITION = (400, "ATLAS-400-00-011", "Invalid type definition {0}")
    INVALID_ATTRIBUTE_TYPE_FOR_CARDINALITY = (400, "ATLAS-400-00-012", "Cardinality of attribute {0}.{1} requires a list or set type")
    ATTRIBUTE_UNIQUE_INVALID = (400, "ATLAS-400-00-013", "Type {0} with unique attribute {1} does not exist")
    TYPE_CATEGORY_INVALID = (400, "ATLAS-400-00-015", "Type Category {0} is invalid")
    INVALID_PARAMETERS = (400, "ATLAS-400-00-01A", "invalid parameters: {0}")
    CLASSIFICATION_ALREADY_ASSOCIATED = (400, "ATLAS-400-00-01B", "instance {0} already is associated with classification {1}")
    INVALID_OBJECT_ID = (400, "ATLAS-400-00-021", "ObjectId is not valid {0}")
    UNKNOWN_ATTRIBUTE = (400, "ATLAS-400-00-023", "Attribute {0} not found for type {1}")
    INVALID_VALUE = (400, "ATLAS-400-00-028", "invalid value: {0}")
    BAD_REQUEST = (400, "ATLAS-400-00-029", "{0}")
    MISSING_MANDATORY_ATTRIBUTE = (400, "ATLAS-400-00-02B", "Mandatory field {0}.{1} has empty/null value")
    INVALID_RELATIONSHIP_END_TYPE = (400, "ATLAS-400-00-036", "invalid relationshipDef: {0}: actual: [end type 1: {1}, end type 2: {2}]. expected: [end type 1: {3}, end type 2: {4}]")
    RELATIONSHIPDEF_INVALID = (400, "ATLAS-400-00-044", "Invalid relationshipDef: {0}")
    UNKNOWN_CLASSIFICATION = (400, "ATLAS-400-00-046", "{0}: Unknown/invalid classification")
    INVALID_SEARCH_PARAMS = (400, "ATLAS-400-00-047", "No search parameter was found. One of the following MUST be specified in the request; typeName, classification, termName or queryText")
    INVALID_RELATIONSHIP_TYPE = (400, "ATLAS-400-00-049", "Invalid entity type '{0}', guid '{1}' in relationship search")
    INVALID_ENTITY_FOR_CLASSIFICATION = (400, "ATLAS-400-00-055", "Entity (guid='{0}',typename='{1}') cannot be classified by Classification '{2}', because '{1}' is not in the ClassificationDef's restrictions.")
    INVALID_DSL_QUERY = (400, "ATLAS-400-00-059", "Invalid DSL query: {0} | Reason: {1}. Please refer to Atlas DSL grammar for more information")
    CLASSIFICATION_UPDATE_FROM_PROPAGATED_ENTITY = (400, "ATLAS-400-00-06B", "Update to classification {0} is not allowed from propagated entity")
    CLASSIFICATION_DELETE_FROM_PROPAGATED_ENTITY = (400, "ATLAS-400-00-06C", "Delete of classification {0} is not allowed from propagated entity")
    INVALID_PARTIAL_UPDATE_ATTR = (400, "ATLAS-400-00-074", "Invalid attribute {0} for partial update of {1}")
    RELATIONSHIP_END_IS_NULL = (400, "ATLAS-400-00-07D", "Relationship end is invalid. Expected {0} but is NULL")
    INVALID_CUSTOM_ATTRIBUTE_KEY_LENGTH = (400, "ATLAS-400-00-08C", "Invalid key: {0} in custom attribute, key size should not be greater than 50")
    INVALID_LABEL_CHARACTERS = (400, "ATLAS-400-00-090", "Invalid label: {0}, label should contain alphanumeric characters, '_' or '-'")
    BUSINESS_METADATA_NOT_ALLOWED = (400, "ATLAS-400-00-08D", "Business metadata {0} is not applicable to entity type {1}")
    NOT_SUPPORTED = (400, "ATLAS-400-00-0A0", "{0} is not supported yet")
    UNKNOWN_GLOSSARY_TERM = (400, "ATLAS-400-00-06E", "{0}: Unknown/invalid glossary term")
    MISSING_MANDATORY_ANCHOR = (400, "ATLAS-400-00-072", "Mandatory anchor attribute is missing")
    INVALID_NEW_ANCHOR_GUID = (400, "ATLAS-400-00-077", "New Anchor guid cannot be empty/null")
    TERM_DISSOCIATION_MISSING_RELATION_GUID = (400, "ATLAS-400-00-078", "Missing mandatory attribute, TermAssignment relationship guid")
    GLOSSARY_QUALIFIED_NAME_CANT_BE_DERIVED = (400, "ATLAS-400-00-079", "Attributes qualifiedName and name are missing. Failed to derive a unique name for Glossary")
    GLOSSARY_TERM_QUALIFIED_NAME_CANT_BE_DERIVED = (400, "ATLAS-400-00-07A", "Attributes qualifiedName, name & glossary name are missing. Failed to derive a unique name for Glossary term")
    GLOSSARY_CATEGORY_QUALIFIED_NAME_CANT_BE_DERIVED = (400, "ATLAS-400-00-07B", "Attributes qualifiedName, name & glossary name are missing. Failed to derive a unique name for Glossary category")
    INVALID_TERM_RELATION_TO_SELF = (400, "ATLAS-400-00-07E", "Invalid Term relationship: Term cannot have a relationship with self")
    INVALID_CHILD_CATEGORY_DIFFERENT_GLOSSARY = (400, "ATLAS-400-00-07F", "Invalid child category relationship: Child category (guid = {0}) belongs to different glossary")
    INVALID_TERM_DISSOCIATION = (400, "ATLAS-400-00-080", "Given relationshipGuid({0}) is invalid for term (guid={1}) and entity(guid={2})")
    MISSING_TERM_ID_FOR_CATEGORIZATION = (400, "ATLAS-400-00-081", "Term guid can't be empty/null")
    MISSING_CATEGORY_DISPLAY_NAME = (400, "ATLAS-400-00-082", "Category name is empty/null")
    INVALID_DISPLAY_NAME = (400, "ATLAS-400-00-083", "name cannot contain following special chars ('@', '.', '<', '>')")
    TERM_HAS_ENTITY_ASSOCIATION = (400, "ATLAS-400-00-084", "Term (guid={0}) cannot be deleted as it has been assigned to {1} entities.")
    INVALID_FILE_TYPE = (400, "ATLAS-400-00-098", "The provided file type: {0} is not supported. Expected file formats are .csv and .xls.")
    NO_DATA_FOUND = (400, "ATLAS-400-00-09A", "No data found in the uploaded file")
    NOT_VALID_FILE = (400, "ATLAS-400-00-09B", "Invalid {0} file")
    PENDING_TASKS_ALREADY_IN_PROGRESS = (400, "ATLAS-400-00-0A1", "There are already {0} pending tasks in queue")
    UNAUTHENTICATED = (401, "ATLAS-401-00-001", "Authentication required")
    UNAUTHORIZED_ACCESS = (403, "ATLAS-403-00-001", "{0} is not authorized to perform {1}")
    TYPE_NAME_NOT_FOUND = (404, "ATLAS-404-00-001", "Given typename {0} was invalid")
    TYPE_GUID_NOT_FOUND = (404, "ATLAS-404-00-002", "Given type guid {0} was invalid")
    NO_CLASSIFICATIONS_FOUND_FOR_ENTITY = (404, "ATLAS-404-00-003", "No classifications associated with entity: {0}")
    INSTANCE_GUID_NOT_FOUND = (404, "ATLAS-404-00-005", "Given instance guid {0} is invalid/not found")
    INSTANCE_LINEAGE_QUERY_FAILED = (404, "ATLAS-404-00-006", "Instance lineage query failed {0}")
    INSTANCE_CRUD_INVALID_PARAMS = (404, "ATLAS-404-00-007", "Invalid instance creation/updation parameters passed : {0}")
    CLASSIFICATION_NOT_FOUND = (404, "ATLAS-404-00-008", "Given classification {0} was invalid")
    INSTANCE_BY_UNIQUE_ATTRIBUTE_NOT_FOUND = (404, "ATLAS-404-00-009", "Instance {0} with unique attribute {1} does not exist")
    REFERENCED_ENTITY_NOT_FOUND = (404, "ATLAS-404-00-00A", "Referenced entity {0} is not found")
    RELATIONSHIP_GUID_NOT_FOUND = (404, "ATLAS-404-00-00C", "Given relationship guid {0} is invalid/not found")
    INVALID_LINEAGE_ENTITY_TYPE = (404, "ATLAS-404-00-011", "Given instance guid {0} with type {1} is not a valid lineage entity type.")
    INSTANCE_GUID_DELETED = (404, "ATLAS-404-00-012", "Given instance guid {0} has been deleted")
    SAVED_SEARCH_NOT_FOUND = (404, "ATLAS-404-00-00F", "Given search {0} was invalid")
    TYPE_ALREADY_EXISTS = (409, "ATLAS-409-00-001", "Given type {0} already exists")
    TYPE_HAS_REFERENCES = (409, "ATLAS-409-00-002", "Given type {0} has references")
    RELATIONSHIP_ALREADY_EXISTS = (409, "ATLAS-409-00-004", "relationship {0} already exists between entities {1} and {2}")
    SAVED_SEARCH_ALREADY_EXISTS = (409, "ATLAS-409-00-006", "search named {0} already exists for user {1}")
    CONCURRENT_UPDATE = (409, "ATLAS-409-00-00B", "Entity {0} was modified concurrently; please retry")
    INSTANCE_UNIQUE_ATTRIBUTE_CONFLICT = (409, "ATLAS-409-00-00C", "Another entity of type {0} already has {1}={2}")
    GLOSSARY_ALREADY_EXISTS = (409, "ATLAS-409-00-007", "Glossary with name {0} already exists")
    GLOSSARY_TERM_ALREADY_EXISTS = (409, "ATLAS-409-00-009", "Glossary term with qualifiedName {0} already exists")
    GLOSSARY_CATEGORY_ALREADY_EXISTS = (409, "ATLAS-409-00-00A", "Glossary category with qualifiedName {0} already exists")
    GLOSSARY_IMPORT_FAILED = (409, "ATLAS-409-00-011", "Glossary import failed")
    INTERNAL_ERROR = (500, "ATLAS-500-00-001", "Internal server error {0}")

    @property
    def http_status(self) -> int:
        return self.value[0]

    @property
    def code(self) -> str:
        return self.value[1]

    def format(self, *params) -> str:
        msg = self.value[2]
        for i, p in enumerate(params):
            msg = msg.replace("{%d}" % i, str(p))
        return msg


class AtlasBaseException(Exception):
    def __init__(self, error_code: AtlasErrorCode, *params):
        self.error_code = error_code
        self.params = params
        self.message = error_code.format(*params)
        super().__init__(self.message)

    @property
    def http_status(self) -> int:
        return self.error_code.http_status

    def to_json(self) -> dict:
        return {"errorCode": self.error_code.code, "errorMessage": self.message}
