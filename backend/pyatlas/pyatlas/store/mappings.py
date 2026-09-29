"""Elasticsearch index definitions.

These indices hold everything Atlas kept in JanusGraph + Solr (plus the access log):

``<prefix>_typedefs``       one document per type definition (source of truth for the type system)
``<prefix>_entities``       one document per entity: raw Atlas JSON (not indexed) + typed search fields
``<prefix>_relationships``  one document per relationship instance (the graph edges)
``<prefix>_unique``         one document per unique-attribute value; its id enforces uniqueness atomically
``<prefix>_audit``          entity audit events
``<prefix>_access``         logins (Keycloak sessions, UI form logins, API users per day)
``<prefix>_meta``           applied model patches, saved searches, misc. server state

Indexed attribute values live in typed groups so that attributes with the same
name but different types in different entity types never produce a mapping conflict::

    idx.str.<attr>   keyword (+ .text analysed, + .lc lowercase keyword)
    idx.lng.<attr>   long      (int/long/short/byte/date)
    idx.dbl.<attr>   double    (float/double/bigdecimal)
    idx.bool.<attr>  boolean

Business-metadata attributes use the same layout under ``bmidx.<group>.<bm>.<attr>``
and classification attributes under the nested ``tags`` field.
"""
from __future__ import annotations

ANALYSIS = {
    "analyzer": {
        "atlas_text": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": ["atlas_word_delimiter", "flatten_graph", "lowercase"],
        }
    },
    "filter": {
        "atlas_word_delimiter": {
            "type": "word_delimiter_graph",
            "preserve_original": True,
            "split_on_case_change": True,
            "split_on_numerics": False,
        }
    },
    "normalizer": {"lc": {"type": "custom", "filter": ["lowercase"]}},
}

STR_FIELD = {
    "type": "keyword",
    "ignore_above": 4096,
    "fields": {
        "text": {"type": "text", "analyzer": "atlas_text"},
        "lc": {"type": "keyword", "normalizer": "lc", "ignore_above": 4096},
    },
}

DYNAMIC_TEMPLATES = [
    {"idx_str": {"path_match": "*.str.*", "match_mapping_type": "string", "mapping": STR_FIELD}},
    {"idx_lng": {"path_match": "*.lng.*", "match_mapping_type": "long", "mapping": {"type": "long"}}},
    {"idx_dbl": {"path_match": "*.dbl.*", "match_mapping_type": "double", "mapping": {"type": "double"}}},
    {"idx_bool": {"path_match": "*.bool.*", "match_mapping_type": "boolean", "mapping": {"type": "boolean"}}},
]

KW = {"type": "keyword"}
LONG = {"type": "long"}
BOOL = {"type": "boolean"}
RAW = {"type": "object", "enabled": False}

IDX_GROUPS = {
    "type": "object",
    "properties": {
        "str": {"type": "object", "dynamic": True},
        "lng": {"type": "object", "dynamic": True},
        "dbl": {"type": "object", "dynamic": True},
        "bool": {"type": "object", "dynamic": True},
    },
}

ENTITY_MAPPING = {
    "dynamic": False,
    "date_detection": False,
    "numeric_detection": False,
    "dynamic_templates": DYNAMIC_TEMPLATES,
    "properties": {
        "guid": KW,
        "typeName": KW,
        "superTypeNames": KW,
        "status": KW,
        "createdBy": KW,
        "updatedBy": KW,
        "createTime": LONG,
        "updateTime": LONG,
        "version": LONG,
        "homeId": KW,
        "isProxy": BOOL,
        "isIncomplete": BOOL,
        "provenanceType": {"type": "integer"},
        "displayText": STR_FIELD,
        "fulltext": {"type": "text", "analyzer": "atlas_text"},
        "classificationNames": KW,
        "propagatedClassificationNames": KW,
        "allClassificationNames": KW,
        "labels": KW,
        "customAttributesKV": KW,
        "meaningNames": KW,
        "meaningQualifiedNames": KW,
        "meanings": RAW,
        "pendingTasks": KW,
        # raw Atlas payload parts, stored only
        "attributes": RAW,
        "classifications": RAW,
        "propagatedClassifications": RAW,
        "customAttributes": RAW,
        "businessAttributes": RAW,
        # search fields
        "idx": {**IDX_GROUPS, "dynamic": True},
        "bmidx": {"type": "object", "dynamic": True},
        "tags": {
            "type": "nested",
            "dynamic": True,
            "properties": {
                "typeName": KW,
                "source": KW,
                "propagated": BOOL,
                "idx": {"type": "object", "dynamic": True},
            },
        },
    },
}

RELATIONSHIP_MAPPING = {
    "dynamic": False,
    "date_detection": False,
    "numeric_detection": False,
    "dynamic_templates": DYNAMIC_TEMPLATES,
    "properties": {
        "idx": {"type": "object", "dynamic": True},
        "guid": KW,
        "typeName": KW,
        "label": KW,
        "status": KW,
        "end1Guid": KW,
        "end1Type": KW,
        "end2Guid": KW,
        "end2Type": KW,
        "propagateTags": KW,
        "deletedByEntity": BOOL,
        "createdBy": KW,
        "updatedBy": KW,
        "createTime": LONG,
        "updateTime": LONG,
        "version": LONG,
        "homeId": KW,
        "provenanceType": {"type": "integer"},
        "attributes": RAW,
        "blockedPropagatedClassifications": RAW,
    },
}

TYPEDEF_MAPPING = {
    "dynamic": False,
    "properties": {
        "name": KW,
        "guid": KW,
        "category": KW,
        "serviceType": KW,
        "superTypes": KW,
        "updateTime": LONG,
        "def": RAW,
    },
}

UNIQUE_MAPPING = {
    "dynamic": False,
    "properties": {"guid": KW, "typeName": KW, "attribute": KW},
}

AUDIT_MAPPING = {
    "dynamic": False,
    "properties": {
        "entityId": KW,
        "timestamp": LONG,
        "user": KW,
        "action": KW,
        "eventKey": KW,
        "seq": LONG,
        "details": {"type": "text", "index": False},
        "entity": RAW,
        # the entity's type and name at the time of the event (for reports such as "changes per user and type")
        "typeName": KW,
        "entityName": KW,
    },
}

# who used pyatlas when: one document per Keycloak session, per login through the Atlas UI form and per user and
# day for other password (Basic) logins (see pyatlas/access_log.py)
ACCESS_MAPPING = {
    "dynamic": False,
    "properties": {
        "user": KW,
        "timestamp": LONG,
        "method": KW,
        "client": KW,
        "ip": KW,
        "session": KW,
        "groups": KW,
    },
}

META_MAPPING = {
    "dynamic": False,
    "properties": {
        "kind": KW,
        "name": KW,
        "ownerName": KW,
        "guid": KW,
        "updateTime": LONG,
        "value": RAW,
    },
}

INDICES = {
    "typedefs": TYPEDEF_MAPPING,
    "entities": ENTITY_MAPPING,
    "relationships": RELATIONSHIP_MAPPING,
    "unique": UNIQUE_MAPPING,
    "audit": AUDIT_MAPPING,
    "meta": META_MAPPING,
    "access": ACCESS_MAPPING,
}
