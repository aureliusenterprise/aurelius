from typing import List
from m4i_atlas_core.config.config_store import ConfigStore
from m4i_data_dictionary_io.entities.json import Collection, DataAttribute, DataField, Dataset, Source, System
from m4i_data_dictionary_io.functions.create_from_excel import get_ref_and_push
from m4i_data_dictionary_io.entities.json import get_qualified_name
from m4i_data_dictionary_io.sources.kafka.discover_cluster import discover_cluster


def create_source(name: str) -> Source:
  return Source.from_dict({
    "name": name,
    "qualifiedName": name
  })

def create_system(name: str, qualified_name: str) -> System:
  return System.from_dict({
    "name": name,
    "qualifiedName": qualified_name
  })

def create_collection(name: str, system_qualified_name: str, qualified_name: str) -> Collection:
  return Collection.from_dict({
    "name": name,
    "system": system_qualified_name,
    "qualifiedName": qualified_name,
  })

def process_topic(item, collection_qualified_name: str) -> List:
  """Process each topic by creating dataset and field instances."""

  print(type(item))

  elements = []

  dataset_qualified_name = collection_qualified_name + "--" + get_qualified_name(item["name"])
  # Create topic
  elements.append(Dataset.from_dict({
    "name": item["name"],
    "collection": "kafka-broker--default-cluster",
    "qualifiedName": dataset_qualified_name,
  }))

  for field in item["fields"]:
    elements.extend(process_field(field, dataset_qualified_name))

  return elements

def process_field(field, dataset_qualified_name) -> List:
  qualified_name = get_qualified_name(field)

  return [
    DataAttribute.from_dict({
      "name": field,
      "qualifiedName": qualified_name,
    }),
    DataField.from_dict({
      "name": field,
      "dataset": dataset_qualified_name,
      "qualifiedName": dataset_qualified_name + "--" + qualified_name,
      "fieldType": "numeric",
      "attribute": qualified_name
    })
  ]

async def create_from_kafka(access_token: str, store: ConfigStore):

  # Fetch data from kafka
  data = discover_cluster()
  # Create Source, System and Collection
  system_qualified_name = store.get("system.qualified_name")
  collection_qualified_name = store.get("collection.qualified_name")
  instances = [
    create_source(store.get("data.dictionary.path")),
    create_system(store.get("system.name"), system_qualified_name),
    create_collection(store.get("collection.name"), system_qualified_name, collection_qualified_name)
  ]

  # Iterate over topics and fields
  for item in data:
    instances += process_topic(item, collection_qualified_name)

  for i in instances:
    atlas_compatible = i.convert_to_atlas()
    await get_ref_and_push([atlas_compatible], False, access_token)
