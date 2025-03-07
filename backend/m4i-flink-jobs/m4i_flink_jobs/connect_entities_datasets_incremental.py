import json
from typing import Any, List, Mapping, MutableMapping
from elastic_enterprise_search import AppSearch
from m4i_atlas_post_install import get_enterprise_search_key
from kafka import KafkaConsumer
from collections import Counter
from datetime import datetime, timedelta
# from m4i_atlas_core.entities.atlas.core.entity_audit_event.EntityAuditEvent import EntityAuditAction, EntityAuditType, EntityAuditEventBase, EntityAuditEventDefaultsBase

# Elasticsearch configuration
elasticsearch_args = {
    "url": 'http://localhost:3002/',
    "username": "elastic",
    "password": "elasticpw",
}
app_search_api_key = get_enterprise_search_key(elasticsearch_args["url"], elasticsearch_args["username"], elasticsearch_args["password"])
app_search_client = AppSearch(elasticsearch_args["url"], bearer_auth=app_search_api_key)

# Kafka consumer configuration
bootstrap_servers = '127.0.0.1:9092'
topic = 'ATLAS_ENTITIES'
group_id = 'test-group'

def get_documents_by_id(app_search_client: AppSearch, engine_name: str, documents: List[str]) -> List[MutableMapping[str, Any]]:
  response = app_search_client.get_documents(
      engine_name=engine_name, document_ids=documents
  )
  return response # type: ignore


def init_consumer():
  consumer = KafkaConsumer(
      topic,
      bootstrap_servers=bootstrap_servers,
      group_id=group_id,
      enable_auto_commit=False,
      auto_offset_reset='earliest'
  )
  consumer.poll(max_records=1)
  return consumer

def get_offset_by_timestamp(consumer, timestamp):
  partitions = consumer.assignment()
  partition_to_timestamp = {part: timestamp for part in partitions}
  return consumer.offsets_for_times(partition_to_timestamp)


def consume_messages(consumer, offsets_for_times):
  """
  Returns the list of messages that are available in this consumer, starting from the given offsets / times
  """
  if offsets_for_times is not None:
    for part, offset in offsets_for_times.items():
      if offset is None:
        # No offset returned for this timestamp -> no messages to consume
        return []
      else:
        print("Seeking to offset", offset.offset)
        consumer.seek(part, offset.offset)

  messages = []
  res = consumer.poll(timeout_ms=5000,max_records=100)
  for consumerrecord in res.values():
    for record in consumerrecord:
      messages.append(record.value)

  consumer.close()
  return messages


def process_message(change_message: MutableMapping[str, Any]):
  """"
  Extract from the given message the GUID(s) and their type(s)
  """
  guids = {}
  if "ENTITY" in change_message['operationType']:
    entity_type = change_message['entity']['typeName']
    guid = change_message['entity']['guid']
    guids[guid] = entity_type
  elif "RELATIONSHIP" in change_message['operationType']:
    #  in [EntityAuditAction.RELATIONSHIP_CREATE, EntityAuditAction.RELATIONSHIP_UPDATE, EntityAuditAction.RELATIONSHIP_DELETE]
    type_1 = change_message['relationship']['end1']['typeName']
    type_2 = change_message['relationship']['end2']['typeName']
    guid_1 = change_message['relationship']['end1']['guid']
    guid_2 = change_message['relationship']['end2']['guid']
    guids[guid_1] = type_1
    guids[guid_2] = type_2
  return guids

def get_derived_entities_incremental(dataset):
  """
  Taking the dataset object, find the data entities that are linked to it by mapping from:
  dataset -> each of its fields -> each of its attributes -> entities associated with the attribute

  Returns two lists -
  - a list of all entities (documents) connected to this entity
  - a list of entity guids indicating which of those datasets have been selected
  """
  derived_entity_guids = []
  attribute_guids = {}

  if dataset["derivedfieldguid"] is not None:
    derived_fields = get_documents_by_id(app_search_client, "atlas-dev", dataset["derivedfieldguid"])
    for field in derived_fields:
      if field["deriveddataattributeguid"] is not None:
        derived_attributes = get_documents_by_id(app_search_client, "atlas-dev", field["deriveddataattributeguid"])
        for attribute in derived_attributes:
          attribute_guids[attribute["guid"]] = 0
          derived_entity_guids.extend(attribute["deriveddataentityguid"])

  entities_attribute_coverage = {}
  entities = {}
  for entity_guid, ct in Counter(derived_entity_guids).most_common():
    entity = get_documents_by_id(app_search_client, "atlas-dev", [entity_guid])[0]
    entities[entity_guid] = entity
    coverage = 0
    for attribute_guid in attribute_guids:
      if attribute_guid in entity["deriveddataattributeguid"] and attribute_guids[attribute_guid] != 1:
        attribute_guids[attribute_guid] = 1
        coverage += 1
    entities_attribute_coverage[entity_guid] = coverage

  derived_entity_guids = [entity_guid for entity_guid, coverage in entities_attribute_coverage.items() if coverage > 0]
  return entities, derived_entity_guids


def connect_dataset_with_entities_incremental(dataset_guid):
  """
  Find the datasets connected with this entity and create the link (by updating the derived GUIDs) of the entity and its datasets,
  then push the changes to ElasticSearch
  """
  dataset = get_documents_by_id(app_search_client, "atlas-dev", [dataset_guid])[0]
  to_index : Mapping[str, Any] = {}

  entities, derived_entity_guids = get_derived_entities_incremental(dataset)
  dataset["deriveddataentityguid"] = derived_entity_guids
  print("Linking dataset: " + dataset['name'] + " with its")
  for guid in derived_entity_guids:
    entities[guid]["deriveddatasetguid"].append(dataset_guid)
    to_index[guid] = entities[guid]

  to_index[dataset_guid] = dataset
  print("Pushing changes to ES")
  response = app_search_client.index_documents(engine_name="atlas-dev", documents=list(to_index.values()))
  print(response)

def get_derived_datasets_incremental(entity):
  """
  Taking the data entity object, find the datasets that are linked to it by mapping from:
  data entity -> each of its data attributes -> each of its fields -> datasets associated with the field
  If the entity has child entities, this also includes recursion to find the datasets associated with the children.

  Returns two lists -
  - a list of all datasets (documents) connected to this entity
  - a list of dataset guids indicating which of those datasets have been selected
  """

  derived_dataset_guids = [] # List of the dataset guids that are linked to this entity
  field_guids = {} # Keep track of the fields that are linked to this entity.

  # Check if the entity has derived entities
  if entity["deriveddataentityguid"] is not None and len(entity["deriveddataentityguid"]) > 0:
      derived_data_entities = get_documents_by_id(app_search_client, "atlas-dev", entity["deriveddataentityguid"])
      for derived_entity in derived_data_entities:
          # Check whether the derived entity is a child by looking at its parentguid
          if derived_entity["parentguid"] == entity["guid"]:
            child_entity = derived_entity
            # Recursively find the datasets associated with the child entity
            return get_derived_datasets_incremental(child_entity)

  # Otherwise, the entity should have data attributes,
  # from which we can derive fields and datasets
  if entity["deriveddataattributeguid"] is not None and len(entity["deriveddataattributeguid"]) > 0:
    attributes = get_documents_by_id(app_search_client, "atlas-dev", entity["deriveddataattributeguid"])
    for attribute in attributes:
        fields = get_documents_by_id(app_search_client, "atlas-dev", attribute["derivedfieldguid"])
        for field in fields:
            # Track the field by adding it to the field_guid dictionary
            field_guids[field["guid"]] = 0
            derived_dataset_guids.extend(field["deriveddatasetguid"])
  else:
    raise Exception("Entity has neither child entities nor child attributes")

  datasets_field_coverage = {} # Track how many fields this dataset covers
  datasets = {}
  # Iterate in order of most commonly linked datasets
  for dataset_guid, ct in Counter(derived_dataset_guids).most_common():
    dataset = get_documents_by_id(app_search_client, "atlas-dev", [dataset_guid])[0]
    datasets[dataset_guid] = dataset
    coverage = 0
    # Mark the fields as covered by this dataset by setting field_guid to 1
    for field_guid in field_guids:
      if field_guid in dataset["derivedfieldguid"] and field_guids[field_guid] != 1:
        field_guids[field_guid] = 1
        coverage += 1
    # Save the coverage of this dataset
    datasets_field_coverage[dataset_guid] = coverage

  # Return the datasets whose field coverage is larger than zero
  derived_dataset_guids = [dataset_guid for dataset_guid, coverage in datasets_field_coverage.items() if coverage > 0]
  return datasets, derived_dataset_guids

def connect_entity_with_datasets_incremental(entity_guid):
  """
  Find the entities connected with this dataset and create the link (by updating the derived GUIDs) of the dataset and its entities,
  then push the changes to ElasticSearch
  """
  entity = get_documents_by_id(app_search_client, "atlas-dev", [entity_guid])[0]
  to_index : Mapping[str, Any] = {}

  # Link the entity with the datasets
  datasets, derived_dataset_guids = get_derived_datasets_incremental(entity)
  entity["deriveddatasetguid"] = derived_dataset_guids
  print("Linking entity: " + entity['name'] + " with its")
  # Link the datasets to the entity
  for guid in derived_dataset_guids:
    datasets[guid]["deriveddataentityguid"].append(entity_guid)
    to_index[guid] = datasets[guid]

  # Save the changes by indexing the changed documents
  to_index[entity_guid] = entity
  print("Pushing changes to ES")
  response = app_search_client.index_documents(engine_name="atlas-dev", documents=list(to_index.values()))
  print(response)

def main():

  # TODO define timestamp or get offset from the last time the job ran
  # from_date = (datetime.now())#  - timedelta(days=1) # e.g. 1 day
  # from_date_ts = int(from_date.timestamp()* 1000) # millisecond timestamps
  consumer = init_consumer()
  offsets_for_times = get_offset_by_timestamp(consumer, 1741272555500)
  print(offsets_for_times)
  messages = consume_messages(consumer, offsets_for_times)

  # # List all the documents that are mentioned in the change messages
  changed_documents = {}
  for message in messages:
    changed_documents.update(process_message(json.loads(message)['message']))
    # changed_documents.update(process_message(json.loads(message.value.decode('utf-8'))))

  # # Make the appropriate changes
  for guid in changed_documents.keys():
    if changed_documents[guid] == "m4i_entity":
      print("Need to update entity")
      connect_entity_with_datasets_incremental(guid)

    elif changed_documents[guid] == "m4i_dataset":
      print("Need to update dataset")
      connect_dataset_with_entities_incremental(guid)

    elif changed_documents[guid] == "m4i_field":
      field = get_documents_by_id(app_search_client, "atlas-dev", [guid])[0]
      for datasetguid in field['deriveddatasetguid']:
        print("Need to update dataset")
        connect_dataset_with_entities_incremental(datasetguid)

    elif changed_documents[guid] == "m4i_data_attribute":
      print("Need to update attribute")
      attribute = get_documents_by_id(app_search_client, "atlas-dev", [guid])[0]
      for entityguid in attribute["deriveddataentityguid"]:
        print("Need to update entity")
        connect_entity_with_datasets_incremental(entityguid)

    else:
      print("No changes made.")

if __name__ == "__main__":
  main()

