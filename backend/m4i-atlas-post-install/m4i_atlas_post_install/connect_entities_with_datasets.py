from pathlib import Path
from typing import Set
import json
from typing import Any, MutableMapping
from collections import Counter
from elastic_enterprise_search import AppSearch
from m4i_atlas_post_install import (
    index_documents,
    index_all_documents,
    load_documents,
    get_enterprise_search_key
)

INPUT = "../data/atlas-dev.json"
OUTPUT = "../data/atlas-dev-index.json"
TOP_K = 5
USE_TOP_K = True

def get_derived_datasets(entity, atlas_dev_index : MutableMapping[str, Any]):
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
      for derived_entity_guid in entity["deriveddataentityguid"]:
          derived_entity = atlas_dev_index[derived_entity_guid]
          # Check whether the derived entity is a child by looking at its parentguid
          if derived_entity["parentguid"] == entity["guid"]:
            child_entity = derived_entity
            # Recursively find the datasets associated with the child entity
            return get_derived_datasets(child_entity, atlas_dev_index)

  # Otherwise, the entity should have data attributes,
  # from which we can derive fields and datasets
  if entity["deriveddataattributeguid"] is not None:
    for attribute_guid in entity["deriveddataattributeguid"]:
        for field_guid in atlas_dev_index[attribute_guid]["derivedfieldguid"]:
            field = atlas_dev_index[field_guid]
            # Track the field by adding it to the field_guid dictionary
            field_guids[field_guid] = 0
            # TODO implicit assumption that the fields are correctly assigned the derived dataset guid
            derived_dataset_guids.extend(field["deriveddatasetguid"])
  else:
    raise Exception("Entity has neither child entities nor child attributes")

  datasets_field_coverage = {} # Track how many fields this dataset covers
  # Iterate in order of most commonly linked datasets
  for dataset_guid, ct in Counter(derived_dataset_guids).most_common():
    dataset = atlas_dev_index[dataset_guid]
    coverage = 0
    # Mark the fields as covered by this dataset by setting field_guid to 1
    for field_guid in field_guids:
      if field_guid in dataset["derivedfield"] and field_guids[field_guid] != 1:
        field_guids[field_guid] = 1
        coverage += 1
    # Save the coverage of this dataset
    datasets_field_coverage[dataset_guid] = coverage

  # Return the top k datasets that have the highest coverage
  derived_dataset_guids = []
  for dataset_guid, coverage in sorted(datasets_field_coverage.items(), key=lambda x: x[1], reverse=True)[:TOP_K]:
    derived_dataset_guids.append(dataset_guid)
  return derived_dataset_guids

def update_index(atlas_dev_index: MutableMapping[str, Any], object_guid, key, value):
  existing_value = atlas_dev_index[object_guid][key]
  if existing_value is not None:
     atlas_dev_index[object_guid][key] = list(set(existing_value + value))
  else:
    atlas_dev_index[object_guid][key] = value

def connect_entities_with_datasets(documents, atlas_dev_index: MutableMapping[str, Any]):
  """
  For each entity, find the datasets linked to it and update the indices of both the entity and the dataset
  """
  for document in documents:
      if document["typename"] == "m4i_data_entity":
        derived_dataset_guids = get_derived_datasets(document, atlas_dev_index)

        derived_dataset_names = [atlas_dev_index[guid]["name"] for guid in derived_dataset_guids]
        print(f"Entity {document['name']} has derived datasets: {derived_dataset_names}")

        # Update the entity by adding its derived datasets
        update_index(atlas_dev_index, document["guid"], "deriveddataset", derived_dataset_names)
        update_index(atlas_dev_index, document["guid"], "deriveddatasetguid", derived_dataset_guids)

        # Update each of the datasets by adding its derived entities
        for dataset_guid in derived_dataset_guids:
          update_index(atlas_dev_index, dataset_guid, "deriveddataentity", [document["name"]])
          update_index(atlas_dev_index, dataset_guid, "deriveddataentityguid", [document["guid"]])


def main():

  # Load documents
  documents = load_documents(Path(INPUT))
  atlas_dev_index = index_documents(documents)

  # Connect entities with datasets
  connect_entities_with_datasets(documents, atlas_dev_index)

  # TODO backwards mapping
  # TODO find out what is TF/IDF and how to use it
  # TODO compute coverage of datasets over fields
  """
  for each entity:
  - get all its fields by branching out
  - make a dictionary of each field and its dataset(s)
  - which group of datasets would, when selected, cover the most fields?
  """

  # Save updated index to file
  new_documents = list(atlas_dev_index.values())
  with open(OUTPUT, "w") as f:
    json.dump(new_documents, f, indent=4)

  # Update index in Elasticsearch
  # app_search_api_key = get_enterprise_search_key(
  #       args.url, args.username, args.password
  #   )
  # app_search_client = AppSearch(args.url, bearer_auth=app_search_api_key)
  # index_all_documents(
  #       app_search_client=app_search_client,
  #       engine_name="atlas-dev",
  #       documents=list(atlas_dev_index.values()),
  #   )

if __name__ == "__main__":
    main()
