import json
from typing import Any, List, Mapping, MutableMapping
from elastic_enterprise_search import AppSearch
from m4i_atlas_post_install import get_enterprise_search_key
from kafka import KafkaConsumer
from collections import Counter
# from m4i_flink_jobs.connect_entities_with_datasets import get_derived_datasets_incremental
# from m4i_atlas_core.entities.atlas.core.entity_audit_event.EntityAuditEvent import EntityAuditAction, EntityAuditType, EntityAuditEventBase, EntityAuditEventDefaultsBase

# Elasticsearch configuration
elasticsearch_args = {
    "url": 'http://localhost:3002/',
    "username": "elastic",
    "password": "elasticpw",
}
# elasticsearch_args = {
#     "url": "https://aureliusdev.westeurope.cloudapp.azure.com/test-namespace/app-search/",
#     "username": "elastic",
#     "password": "5I25YUNdcp17Scc8y6O9Qf54",
# }
app_search_api_key = get_enterprise_search_key(elasticsearch_args["url"], elasticsearch_args["username"], elasticsearch_args["password"])
app_search_client = AppSearch(elasticsearch_args["url"], bearer_auth=app_search_api_key)

# Kafka consumer configuration
bootstrap_servers = '127.0.0.1:9092'
topic = 'ATLAS_ENTITIES'
group_id = 'my-group'

# consumer_config = {
#         "auto.offset.reset": "earliest",
#         "bootstrap.servers": bootstrap_servers,
#         "enable.auto.commit": False,
#         "group.id": group_id,
#         "sasl.mechanisms": "PLAIN",
#         "sasl.password": password,
#         "sasl.username": username,
#         "security.protocol": "SASL_SSL"
#     }

def get_documents_by_id(app_search_client: AppSearch, engine_name: str, documents: List[str]) -> List[MutableMapping[str, Any]]:
  response = app_search_client.get_documents(
      engine_name=engine_name, document_ids=documents
  )
  return response # type: ignore

# documents: List[MutableMapping[str, Any]] = get_documents_by_id(app_search_client, "atlas-dev", ["fed7d6b6-3a49-4c48-b7fa-fda76a1a7d87"]) # type: ignore
# print(documents[0]['deriveddataattribute'])

def consume_messages():
  # WIP - for now, this method is not used
  consumer = KafkaConsumer(
      topic,
      bootstrap_servers=bootstrap_servers,
      group_id=group_id,
      enable_auto_commit=False,
      auto_offset_reset='earliest'
  )
  messages = []
  count = 0
  with open("kafka_messages.txt", "w") as f:
    for message in consumer:
      if count <= 100:
        f.write(message.value.decode('utf-8') + "\n")
        messages.append(message)
        count += 1
      else:
        consumer.close()
        break
  return messages

def get_messages():
  # Temporary for dev/test purpose - read messages from file
  messages = []
  f = open("kafka_messages.txt", "r")
  stop = 0
  for line in f:
      if stop <= 10:
        messages.append(line)
        # change_msg = json.loads(line)['message']
        # guids.update(process_message(change_msg))
        stop += 1
  f.close()
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


def get_derived_datasets_incremental(entity):
  """
  Taking the data entity object, find the datasets that are linked to it by mapping from:
  data entity -> each of its data attributes -> each of its fields -> datasets associated with the field
  If the entity has child entities, this also includes a single recursion to find the datasets associated with the children.
  Returns two lists - a list of dataset names and a list of guids
  """

  derived_dataset_guids = [] # List of the dataset guids that are linked to this entity
  field_guids = {} # Keep track of the fields that are linked to this entity.

  # Check if the entity has derived entities
  if entity["deriveddataentityguid"] is not None:
      derived_data_entities = get_documents_by_id(app_search_client, "atlas-dev", entity["deriveddataentityguid"])
      for derived_entity in derived_data_entities:
          # Check whether the derived entity is a child by looking at its parentguid
          if derived_entity["parentguid"] == entity["guid"]:
            child_entity = derived_entity
            # Recursively find the datasets associated with the child entity
            return get_derived_datasets_incremental(child_entity)

  # Otherwise, the entity should have data attributes,
  # from which we can derive fields and datasets
  if entity["deriveddataattributeguid"] is not None:
    attributes = get_documents_by_id(app_search_client, "atlas-dev", entity["deriveddataattributeguid"])
    for attribute in attributes:
        fields = get_documents_by_id(app_search_client, "atlas-dev", attribute["derivedfieldguid"])
        for field in fields:
            # Track the field by adding it to the field_guid dictionary
            field_guids[field["guid"]] = 0
            # TODO implicit assumption that the fields are correctly assigned the derived dataset guid
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
  entity = get_documents_by_id(app_search_client, "atlas-dev", [entity_guid])[0]
  to_index : List[Mapping[str, Any]] = []

  # Link the entity with the datasets
  datasets, derived_dataset_guids = get_derived_datasets_incremental(entity)
  entity["deriveddatasetguid"] = derived_dataset_guids
  print("Linking entity: " + entity['name'] + " with its")
  # Link the datasets to the entity
  for guid in derived_dataset_guids:
    datasets[guid]["deriveddataentityguid"].append(entity_guid)
    to_index.append({guid : datasets[guid]})

  print("UPDATED!")
  # Save the changes by indexing the changed documents
  # to_index.append({entity_guid : entity})
  # app_search_client.index_documents(engine_name="atlas-dev", documents=to_index)

def main():
  # TODO a proper consumer that reads messages from Kafka
  # consume_messages() # write to file
  consumer = get_messages() # get first 10 messages from file

  # List all the documents that are mentioned in the change messages
  changed_documents = {}
  for message in consumer:
    changed_documents.update(process_message(json.loads(message)['message']))
    # changed_documents.update(process_message(json.loads(message.value.decode('utf-8'))))

  # # Make the appropriate changes
  for guid in changed_documents.keys():
    if changed_documents[guid] == "m4i_entity":
      print("Need to update entity")
      connect_entity_with_datasets_incremental(guid)

    elif changed_documents[guid] == "m4i_dataset":
      print("Need to update dataset")
      # TODO implementation

    elif changed_documents[guid] == "m4i_field":
      print("Need to update field")
      # TODO implementation

    elif changed_documents[guid] == "m4i_data_attribute":
      print("Need to update attribute")
      # TODO implementation

if __name__ == "__main__":
    main()

