"""Lineage registration API (replaces m4i-lineage-rest-api, the Flask service deployment pipelines call).

``GET  /api/lin_api/<namespace>/``  -> ``{"entities": n, "qualifiedNames": [...]}`` of that entity type
``POST /api/lin_api/<namespace>/``  -> registers one entity (processes, Kubernetes objects, Kafka / Elastic /
Kibana objects) and answers ``{"CREATE": n, "UPDATE": n, "DELETE": n}``

The 24 namespaces, payloads and answers are those of the old service (``/lin_api/<namespace>/``, now behind
``/<ns>/lin_api/`` on the reverse proxy).  Each payload is turned into the same Atlas entities the old service
sent to Atlas (checked against the old code: ``tests/data/lineage_api_reference.json``) and stored through the
entity API as the calling user.  ``lineage_api_spec.json`` holds the request schemas of the old service (its
flask-restx models, validated the same way) and the attribute defaults the m4i-atlas-core classes wrote;
``scripts/gen_lineage_api_spec.py`` regenerates it from the old code.

Differences, all where the old service failed: a Kafka topic with a record value schema works (the old one
raised a TypeError for most schemas), Avro types outside its enum (``boolean``, ``bytes``, ``map``...) are kept
as field types instead of failing, a payload that misses a required value answers 400 instead of 500, and
Atlas errors (e.g. a referenced entity that does not exist) keep their status and message instead of a bare 500.
"""
from __future__ import annotations

import copy
import itertools
import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

SPEC = json.loads((Path(__file__).parent / "lineage_api_spec.json").read_text(encoding="utf-8"))
DEFAULTS: Dict[str, dict] = SPEC["defaults"]

_WHITE_SPACE = re.compile(r"[\s]+")
_ILLEGAL = re.compile(r"[&]+")


class PayloadError(ValueError):
    def __init__(self, errors: Dict[str, str]):
        super().__init__("Input payload validation failed")
        self.errors = errors


def qualified_name(*components: Optional[str], prefix: Optional[str] = "") -> str:
    """m4i ``get_qualified_name``: lower case, ``&`` removed, white space -> ``-``, joined by ``--``."""
    parts = [_WHITE_SPACE.sub("-", _ILLEGAL.sub("", c.lower())) for c in components if c]
    qn = "--".join(parts)
    return f"{prefix}--{qn}" if prefix else qn


# ------------------------------------------------------------------ payload access (dataclasses_json rules)
def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Payload:
    """Reads a field by its camelCase or snake_case key (the old dataclasses accepted both; when a payload has
    both, the later one wins, as with dataclasses_json)."""

    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise PayloadError({"": "the payload must be a JSON object"})
        self.data = data

    def get(self, name: str, default: Any = None) -> Any:
        keys = (name, _snake(name))
        found = default
        for k, v in self.data.items():
            if k in keys:
                found = v
        return found

    def req(self, name: str) -> Any:
        v = self.get(name, _MISSING)
        if v is _MISSING:
            raise PayloadError({name: f"'{name}' is a required property"})
        return v

    def text(self, name: str, required: bool = False) -> Optional[str]:
        v = self.req(name) if required else self.get(name)
        return str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v

    def number(self, name: str, required: bool = False) -> Optional[int]:
        v = self.req(name) if required else self.get(name)
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise PayloadError({name: f"'{v}' is not of type 'integer'"}) from None
        return v


_MISSING = object()


class Guids:
    """Placeholder guids (negative numbers) for entities created in one request."""

    def __init__(self):
        self._n = itertools.count(1001)

    def __call__(self) -> str:
        return f"-{next(self._n)}"


def oid(type_name: str, qn: str, guid: Optional[str] = None) -> dict:
    ref = {"typeName": type_name, "uniqueAttributes": {"qualifiedName": qn}}
    if guid is not None:
        ref["guid"] = guid
    return ref


def refs(values, type_name: str) -> List[dict]:
    """One reference per qualified name (a single string counts as one)."""
    if isinstance(values, str):
        values = [values]
    return [oid(type_name, v) for v in values or []]


def entity(type_name: str, guid: str, **attributes) -> dict:
    """The entity as the m4i-atlas-core class serialised it: every attribute of the class (defaults included),
    attributes the class does not know are dropped (e.g. ``source`` of processes was never sent)."""
    attrs = copy.deepcopy(DEFAULTS[type_name])
    attrs.update((k, v) for k, v in attributes.items() if k in attrs)
    return {"typeName": type_name, "guid": guid, "attributes": attrs}


Converted = Tuple[List[dict], Dict[str, dict]]


# ------------------------------------------------------------------ processes
def _process_attrs(p: Payload, *, source: bool = True, owner: bool = True) -> dict:
    a = {"name": p.text("name", True), "qualifiedName": p.text("qualifiedName", True),
         "description": p.text("description"), "inputs": refs(p.get("inputs") or [], "m4i_dataset"),
         "outputs": refs(p.get("outputs") or [], "m4i_dataset")}
    if owner and p.get("processOwner"):
        a["processOwner"] = refs(p.get("processOwner"), "m4i_person")
    if source and p.get("source"):
        a["source"] = refs(p.get("source"), "m4i_source")
    return a


def generic_process(p: Payload, g: Guids) -> Converted:
    p.req("inputs"), p.req("outputs")
    return [entity("m4i_generic_process", g(), **_process_attrs(p))], {}


def microservice_process(p: Payload, g: Guids) -> Converted:
    a = _process_attrs(p)
    system = p.text("system", True)
    if system:
        a["system"] = refs(system, "m4i_kubernetes_pod")
    return [entity("m4i_microservice_process", g(), **a)], {}


def connector_process(p: Payload, g: Guids) -> Converted:
    p.req("inputs"), p.req("outputs")
    a = _process_attrs(p)
    a.update(connectorType=p.text("connectorType", True), server=p.text("server", True))
    return [entity("m4i_connector_process", g(), **a)], {}


def api_operation_process(p: Payload, g: Guids) -> Converted:
    a = _process_attrs(p, source=False)
    ms = p.text("microservice", True)
    if ms:
        a["microservice"] = refs(ms, "m4i_microservice_process")
    return [entity("m4i_api_operation_process", g(), **a)], {}


def ingress_controller_process(p: Payload, g: Guids) -> Converted:
    a = _process_attrs(p, source=False)
    if p.get("ingressObject"):
        a["ingressObject"] = refs(p.get("ingressObject"), "m4i_ingress_object_process")
    e = entity("m4i_ingress_controller_process", g(), **a)
    e["relationshipAttributes"] = {"cluster": refs(p.text("cluster", True), "m4i_kubernetes_cluster")}
    return [e], {}


def ingress_object_process(p: Payload, g: Guids) -> Converted:
    a = _process_attrs(p, source=False)
    if p.get("kubernetesService"):
        a["kubernetesService"] = refs(p.get("kubernetesService"), "m4i_kubernetes_service_process")
    if p.get("ingressController"):
        a["ingressController"] = refs(p.get("ingressController"), "m4i_ingress_controller_process")
    e = entity("m4i_ingress_object_process", g(), **a)
    e["relationshipAttributes"] = {"namespace": refs(p.text("namespace", True), "m4i_kubernetes_namespace")}
    return [e], {}


def kubernetes_service_process(p: Payload, g: Guids) -> Converted:
    a = _process_attrs(p, source=False)
    if p.get("ingressObject"):
        a["ingressObject"] = refs(p.get("ingressObject"), "m4i_ingress_object_process")
    if p.get("microservice"):
        a["microservice"] = refs(p.get("microservice"), "m4i_microservice_process")
    e = entity("m4i_kubernetes_service_process", g(), **a)
    e["relationshipAttributes"] = {"namespace": refs(p.text("namespace", True), "m4i_kubernetes_namespace")}
    return [e], {}


# ------------------------------------------------------------------ Kubernetes
def _k8s_attrs(p: Payload) -> dict:
    return {"name": p.text("name", True), "qualifiedName": p.text("qualifiedName", True),
            "definition": p.text("description")}


def _optional_refs(a: dict, p: Payload, key: str, type_name: str) -> None:
    if p.get(key):
        a[key] = refs(p.get(key), type_name)


def kubernetes_environment(p: Payload, g: Guids) -> Converted:
    a = _k8s_attrs(p)
    _optional_refs(a, p, "kubernetesClusters", "m4i_kubernetes_cluster")
    return [entity("m4i_kubernetes_environment", g(), **a)], {}


def kubernetes_cluster(p: Payload, g: Guids) -> Converted:
    a = _k8s_attrs(p)
    a["kubernetesEnvironment"] = refs(p.text("kubernetesEnvironment", True), "m4i_kubernetes_environment")
    _optional_refs(a, p, "kubernetesNamespace", "m4i_kubernetes_namespace")
    return [entity("m4i_kubernetes_cluster", g(), **a)], {}


def kubernetes_namespace(p: Payload, g: Guids) -> Converted:
    a = _k8s_attrs(p)
    a["kubernetesCluster"] = refs(p.text("kubernetesCluster", True), "m4i_kubernetes_cluster")
    _optional_refs(a, p, "kubernetesDeployment", "m4i_kubernetes_deployment")
    _optional_refs(a, p, "kubernetesCronjob", "m4i_kubernetes_cronjob")
    return [entity("m4i_kubernetes_namespace", g(), **a)], {}


def kubernetes_deployment(p: Payload, g: Guids) -> Converted:
    a = _k8s_attrs(p)
    a["kubernetesNamespace"] = refs(p.text("kubernetesNamespace", True), "m4i_kubernetes_namespace")
    a["tags"] = p.text("tags")
    _optional_refs(a, p, "kubernetesPod", "m4i_kubernetes_pod")
    return [entity("m4i_kubernetes_deployment", g(), **a)], {}


def kubernetes_cronjob(p: Payload, g: Guids) -> Converted:
    a = _k8s_attrs(p)
    a["kubernetesNamespace"] = refs(p.text("kubernetesNamespace", True), "m4i_kubernetes_namespace")
    a.update(tags=p.text("tags"), schedule=p.text("schedule"))
    _optional_refs(a, p, "kubernetesPod", "m4i_kubernetes_pod")
    return [entity("m4i_kubernetes_cronjob", g(), **a)], {}


def kubernetes_pod(p: Payload, g: Guids) -> Converted:
    a = _k8s_attrs(p)
    a["replicas"] = p.text("replicas")
    _optional_refs(a, p, "kubernetesDeployment", "m4i_kubernetes_deployment")
    _optional_refs(a, p, "kubernetesCronjob", "m4i_kubernetes_cronjob")
    _optional_refs(a, p, "microservice", "m4i_microservice_process")
    return [entity("m4i_kubernetes_pod", g(), **a)], {}


# ------------------------------------------------------------------ Confluent / Kafka / Elastic / Kibana
def confluent_cloud(p: Payload, g: Guids) -> Converted:
    name = p.text("name", True)
    a = {"name": name, "qualifiedName": qualified_name(name)}
    _optional_refs(a, p, "confluentEnvironment", "m4i_confluent_environment")
    return [entity("m4i_confluent_cloud", g(), **a)], {}


def confluent_environment(p: Payload, g: Guids) -> Converted:
    name, cloud = p.text("name", True), p.text("confluentCloud")
    a = {"name": name, "schemaRegistry": p.get("schemaRegistry", False),
         "confluentCloud": [oid("m4i_confluent_cloud", cloud)], "qualifiedName": qualified_name(name, prefix=cloud)}
    return [entity("m4i_confluent_environment", g(), **a)], {}


def kafka_cluster(p: Payload, g: Guids) -> Converted:
    name, env = p.text("name", True), p.text("confluentEnvironment", True)
    a = {"name": name, "kafkaPartitions": p.text("kafkaPartitions"), "kafkaReplicas": p.text("kafkaReplicas"),
         "confluentEnvironment": refs(env, "m4i_confluent_environment"), "qualifiedName": qualified_name(name, prefix=env)}
    return [entity("m4i_kafka_cluster", g(), **a)], {}


def elastic_cluster(p: Payload, g: Guids) -> Converted:
    name = p.text("name", True)
    a = {"name": name, "shardCount": p.number("shardCount"), "replicaCount": p.number("replicaCount"),
         "qualifiedName": qualified_name(name)}
    return [entity("m4i_elastic_cluster", g(), **a)], {}


def kibana_space(p: Payload, g: Guids) -> Converted:
    name, cluster = p.text("name", True), p.text("elasticCluster", True)
    cl = [oid("m4i_elastic_cluster", cluster)]
    a = {"name": name, "systems": cl, "elasticCluster": copy.deepcopy(cl), "avatarColor": p.text("avatarColor"),
         "avatarInitials": p.text("avatarInitials"), "definition": p.text("definition"),
         "qualifiedName": qualified_name(name, prefix=cluster)}
    return [entity("m4i_kibana_space", g(), **a)], {}


def ksql(p: Payload, g: Guids) -> Converted:
    name = p.text("name", True)
    a = {"name": name, "kafkaTopic": refs(p.text("kafkaTopic", True), "m4i_kafka_topic"),
         "valueFormat": p.text("valueFormat"), "query": p.text("query"), "properties": p.text("properties"),
         "qualifiedName": qualified_name(name, prefix=f"{p.text('env')}--{p.text('cluster')}")}
    return [entity("m4i_ksql", g(), **a)], {}


# ------------------------------------------------------------------ Kibana saved objects
def dashboard(p: Payload, g: Guids) -> Converted:
    a = {"name": p.text("name", True), "qualifiedName": qualified_name(p.text("qualifiedName", True)),
         "updatedAt": p.text("updatedAt"), "version": p.text("version")}
    _optional_refs(a, p, "childDataset", "m4i_visualization")
    _optional_refs(a, p, "creator", "m4i_person")
    if p.get("kibanaSpace"):
        a["kibanaSpace"] = [oid("m4i_kibana_space", p.text("kibanaSpace"))]
    return [entity("m4i_dashboard", g(), **a)], {}


def visualization(p: Payload, g: Guids) -> Converted:
    a = {"name": p.text("name", True), "qualifiedName": qualified_name(p.text("qualifiedName", True)),
         "type": p.text("type"), "updatedAt": p.text("updatedAt"), "version": p.text("version"),
         "visualizationType": p.text("visualizationType")}
    _optional_refs(a, p, "childDataset", "m4i_index_pattern")
    _optional_refs(a, p, "parentDataset", "m4i_dashboard")
    _optional_refs(a, p, "creator", "m4i_person")
    return [entity("m4i_visualization", g(), **a)], {}


def index_pattern(p: Payload, g: Guids) -> Converted:
    a = {"name": p.text("name", True), "qualifiedName": qualified_name(p.text("qualifiedName", True)),
         "updatedAt": p.text("updatedAt"), "version": p.text("version"), "description": p.text("description"),
         "parentDataset": refs(p.get("parentDataset"), "m4i_visualization") if p.get("parentDataset") else None,
         "creator": refs(p.get("creator"), "m4i_person") if p.get("creator") else None}
    return [entity("m4i_index_pattern", g(), **a)], {}


# ------------------------------------------------------------------ datasets with fields
def _collection(qn: str, system: dict) -> Tuple[dict, Dict[str, dict]]:
    ref = {"guid": "-1", "typeName": "m4i_collection", "uniqueAttributes": {"qualifiedName": qn}}
    return ref, {"-1": {"guid": "-1", "typeName": "m4i_collection",
                        "attributes": {"qualifiedName": qn, "systems": [system], "name": qn}}}


def _attribute_refs(doc) -> List[dict]:
    return refs([doc] if isinstance(doc, str) else list(doc), "m4i_data_attribute")


AVRO_NULL = "null"


def _avro_children(f: dict) -> List[dict]:
    t = f.get("type")
    out = []
    if isinstance(t, dict):
        out.append(t)
    if isinstance(t, list):
        out += [x for x in t if isinstance(x, dict)]
    return out + list(f.get("fields") or [])


def _avro_type(f: dict) -> Optional[str]:
    if f.get("logicalType") is not None:
        return f["logicalType"]
    t = f.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != AVRO_NULL), None)
    if t is None:
        return None
    if isinstance(t, dict):
        return "record"
    return t if isinstance(t, str) else None


def _kafka_field(f: dict, topic_qn: str, topic_guid: str, g: Guids, parent_qn: Optional[str] = None,
                 parent_guid: Optional[str] = None) -> Tuple[dict, List[dict]]:
    if not isinstance(f, dict) or "type" not in f:
        raise PayloadError({"value_schema": "every field needs a type"})
    qn = qualified_name(f.get("name"), prefix=parent_qn if parent_qn is not None else topic_qn)
    a = {"qualifiedName": qn, "name": f.get("name"), "fieldType": _avro_type(f),
         "datasets": [oid("m4i_kafka_topic", topic_qn, topic_guid)]}
    if f.get("doc"):
        a["attributes"] = _attribute_refs(f["doc"])
    if parent_qn is not None:
        a["parentField"] = [oid("m4i_kafka_field", parent_qn, parent_guid)]
        a["datasets"] = None
    field = entity("m4i_kafka_field", g(), **a)
    referred = copy.deepcopy(field)
    children, child_refs = [], []
    for c in _avro_children(f):
        ce, crefs = _kafka_field(c, topic_qn, topic_guid, g, qn, field["guid"])
        children.append(ce)
        child_refs += crefs
    referred["attributes"]["childField"] = children
    return field, [referred, *child_refs]


def kafka_topic(p: Payload, g: Guids) -> Converted:
    name, cluster, env = p.text("name", True), p.text("cluster", True), p.text("environment")
    replicas, partitions = p.number("replicas", True), p.number("partitions", True)
    p.req("keySchema")
    value_schema = p.req("valueSchema")
    topic_qn = f"{env}--{cluster}--{name}"
    collection, referred = _collection(f"{env}--{cluster}--data", oid("m4i_kafka_cluster", f"{env}--{cluster}"))
    topic = entity("m4i_kafka_topic", g(), name=name, collections=[collection], partitions=partitions,
                   replicas=replicas, qualifiedName=topic_qn)
    if not isinstance(value_schema, str):
        if not isinstance(value_schema, dict) or not isinstance(value_schema.get("fields"), list):
            raise PayloadError({"value_schema": "expected a schema string or {\"fields\": [...]}"})
        fields = []
        for f in value_schema["fields"]:
            fe, frefs = _kafka_field(f, topic_qn, topic["guid"], g)
            fields.append(fe)
            for r in frefs:
                referred[r["guid"]] = r
        topic["attributes"]["fields"] = fields
    return [topic], referred


def _elastic_fields(props: dict, meta: Any, index_qn: str, index_guid: str, g: Guids,
                    parent_qn: Optional[str] = None, parent_guid: Optional[str] = None) -> Tuple[List[dict], List[dict]]:
    fields, referred = [], []
    for key, prop in props.items():
        prop = prop if isinstance(prop, dict) else {}
        m = meta.get(key) if isinstance(meta, dict) else None
        qn = f"{parent_qn if parent_qn is not None else index_qn}--{key}"
        a = {"qualifiedName": qn, "name": key, "fieldType": prop.get("type"),
             "datasets": [oid("m4i_elastic_index", index_qn, index_guid)]}
        if m is not None and not isinstance(m, dict):
            a["attributes"] = _attribute_refs(m)
        if parent_qn is not None:
            a["parentField"] = [oid("m4i_elastic_field", parent_qn, parent_guid)]
            a["datasets"] = None
        field = entity("m4i_elastic_field", g(), **a)
        ref = copy.deepcopy(field)
        nested_refs: List[dict] = []
        if prop.get("properties"):
            nested, nested_refs = _elastic_fields(prop["properties"], m, index_qn, index_guid, g, qn, field["guid"])
            ref["attributes"]["childField"] = nested
        fields.append(field)
        referred += [ref, *nested_refs]
    return fields, referred


def elastic_index(p: Payload, g: Guids) -> Converted:
    name, qn, cluster = p.text("name", True), p.text("qualifiedName", True), p.text("cluster")
    collection, referred = _collection(f"{cluster}--data", oid("m4i_elastic_cluster", f"{cluster}"))
    index = entity("m4i_elastic_index", g(), name=name, collections=[collection], qualifiedName=qn)
    template = p.get("indexTemplate")
    if template is not None:
        mappings = template.get("mappings") if isinstance(template, dict) else None
        if not isinstance(mappings, dict) or not isinstance(mappings.get("properties"), dict):
            raise PayloadError({"indexTemplate": "expected {\"mappings\": {\"properties\": {...}, \"_meta\": {...}}}"})
        fields, frefs = _elastic_fields(mappings["properties"], mappings.get("_meta") or {}, qn, index["guid"], g)
        index["attributes"]["fields"] = fields
        for r in frefs:
            referred[r["guid"]] = r
    return [index], referred


# ------------------------------------------------------------------ namespaces
NAMESPACES: Dict[str, Tuple[str, Callable[[Payload, Guids], Converted]]] = {
    "process/generic_process": ("m4i_generic_process", generic_process),
    "process/microservice_process": ("m4i_microservice_process", microservice_process),
    "process/connector_process": ("m4i_connector_process", connector_process),
    "process/api_operation_process": ("m4i_api_operation_process", api_operation_process),
    "process/ingress_controller_process": ("m4i_ingress_controller_process", ingress_controller_process),
    "process/ingress_object_process": ("m4i_ingress_object_process", ingress_object_process),
    "process/kubernetes_service_process": ("m4i_kubernetes_service_process", kubernetes_service_process),
    "kubernetes/kubernetes_environment": ("m4i_kubernetes_environment", kubernetes_environment),
    "kubernetes/kubernetes_cluster": ("m4i_kubernetes_cluster", kubernetes_cluster),
    "kubernetes/kubernetes_namespace": ("m4i_kubernetes_namespace", kubernetes_namespace),
    "kubernetes/kubernetes_deployment": ("m4i_kubernetes_deployment", kubernetes_deployment),
    "kubernetes/kubernetes_cronjob": ("m4i_kubernetes_cronjob", kubernetes_cronjob),
    "kubernetes/kubernetes_pod": ("m4i_kubernetes_pod", kubernetes_pod),
    "entity/confluentCloud_entity": ("m4i_confluent_cloud", confluent_cloud),
    "entity/confluentEnvironment_entity": ("m4i_confluent_environment", confluent_environment),
    "entity/kafkaCluster_entity": ("m4i_kafka_cluster", kafka_cluster),
    "entity/elasticCluster_entity": ("m4i_elastic_cluster", elastic_cluster),
    "entity/kibanaSpace_entity": ("m4i_kibana_space", kibana_space),
    "entity/ksql_entity": ("m4i_ksql", ksql),
    "entity/dashboard_entity": ("m4i_dashboard", dashboard),
    "entity/visualization_entity": ("m4i_visualization", visualization),
    "entity/indexPattern_entity": ("m4i_index_pattern", index_pattern),
    "entity/kafkaTopic_entity": ("m4i_kafka_topic", kafka_topic),
    "entity/elasticIndex_entity": ("m4i_elastic_index", elastic_index),
}


def validate(namespace: str, body: Any) -> None:
    """The old service's request validation (flask-restx models, JSON schema draft 4), same error format."""
    ep = SPEC["endpoints"][namespace]
    if not ep.get("validate"):
        return
    from jsonschema import Draft4Validator
    schema = {"definitions": SPEC["definitions"], "$ref": ep["$ref"]}
    validator = Draft4Validator(schema)
    errors = {}
    for e in validator.iter_errors(body):
        path = [str(x) for x in e.path]
        if e.validator == "required":
            m = re.match(r"'(?P<name>.*)' is a required property", e.message)
            if m:
                path.append(m.group("name"))
        errors[".".join(path)] = e.message
    if errors:
        raise PayloadError(errors)


def convert(namespace: str, body: Any) -> Tuple[List[dict], Dict[str, dict]]:
    """Validated payload -> (entities, referred entities) for ``POST /api/atlas/v2/entity/bulk``."""
    validate(namespace, body)
    return NAMESPACES[namespace][1](Payload(body), Guids())


def mutation_counts(response: dict) -> dict:
    mutated = response.get("mutatedEntities") or {}
    return {k: len(mutated.get(k) or []) for k in ("CREATE", "UPDATE", "DELETE")}
