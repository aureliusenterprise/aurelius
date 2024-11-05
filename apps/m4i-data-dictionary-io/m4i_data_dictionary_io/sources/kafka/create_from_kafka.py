from typing import List
from m4i_data_dictionary_io.entities.json import Collection, DataAttribute, DataField, Dataset, Source, System
from m4i_data_dictionary_io.functions.create_from_excel import get_ref_and_push
from m4i_data_dictionary_io.entities.json import get_qualified_name
from m4i_data_dictionary_io.sources.kafka.discover_cluster import discover_cluster


def create_source() -> Source:
  return Source.from_dict({
    "name": "localhost:9092",
    "qualifiedName": "localhost:9092"
  })

def create_system() -> System:
  return System.from_dict({
    "name": "Kafka Broker",
    "qualifiedName": "kafka-broker"
  })

def create_collection() -> Collection:
  return Collection.from_dict({
    "name": "Default Cluster",
    "system": "kafka-broker",
    "qualifiedName": "kafka-broker--default-cluster",
  })

def process_topic(item) -> List:
  """Process each topic by creating dataset and field instances."""

  elements = []

  dataset_qualified_name = "kafka-broker--default-cluster" + "--" + get_qualified_name(item["name"])
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

async def create_from_kafka(access_token: str):

  # Fetch data from kafka
  data = discover_cluster()
  # Create Source, System and Collection
  instances = [
    create_source(),
    create_system(),
    create_collection()
  ]

  # Iterate over topics and fields
  for item in data:
    instances += process_topic(item)

  for i in instances:
    atlas_compatible = i.convert_to_atlas()
    await get_ref_and_push([atlas_compatible], False, access_token)
