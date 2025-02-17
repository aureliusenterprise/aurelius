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

PATH = "../data/atlas-dev.json"
TOP_K = 5
USE_TOP_K = True

def get_derived_datasets(entity, atlas_dev_index : MutableMapping[str, Any], recurse=True):
  """
  Taking the data entity object, find the datasets that are linked to it by mapping from:
  data entity -> each of its data attributes -> each of its fields -> datasets associated with the field
  If the entity has child entities, this also includes a single recursion to find the datasets associated with the children.
  Returns two lists - a list of dataset names and a list of guids
  """
  derived_dataset_names = []
  derived_dataset_guids = []

  # Check if the entity has children - if it does, recurse
  if entity["deriveddataentityguid"] is not None and recurse:
      for child_entity_guid in  entity["deriveddataentityguid"]:
          child_entity = atlas_dev_index[child_entity_guid]
          child_datasets, child_guids = get_derived_datasets(child_entity, atlas_dev_index, recurse=False)
          derived_dataset_names.extend(child_datasets)
          derived_dataset_guids.extend(child_guids)

  # Otherwise, the entity should have data attributes,
  # from which we can derive fields and datasets
  if entity["deriveddataattributeguid"] is not None:
    for attribute_guid in entity["deriveddataattributeguid"]:
        for field_guid in atlas_dev_index[attribute_guid]["derivedfieldguid"]:
            field = atlas_dev_index[field_guid]
            derived_dataset_names.extend(field["deriveddataset"])
            derived_dataset_guids.extend(field["deriveddatasetguid"])
  else:
    raise Exception("Entity has neither child entities nor child attributes")

  return derived_dataset_names, derived_dataset_guids

def update_index(atlas_dev_index: MutableMapping[str, Any], object_guid, key, value):
  existing_value = atlas_dev_index[object_guid][key]
  if existing_value is not None:
     atlas_dev_index[object_guid][key] = list(set(existing_value + value))
  else:
    atlas_dev_index[object_guid][key] = value

def connect_entities_with_datasets(documents, atlas_dev_index: MutableMapping[str, Any]):
  """
  For each entity, find the datasets linked to it and update the indicies of both the entity and the dataset
  Optionally link only the top-k most common datasets per entity.
  """
  for document in documents:
      if document["typename"] == "m4i_data_entity":
        derived_dataset_names, derived_dataset_guids = get_derived_datasets(document, atlas_dev_index)

        if USE_TOP_K:
          guids = []
          for guid, ct in Counter(derived_dataset_guids).most_common(TOP_K):
            guids.append(guid)
          derived_dataset_guids = guids
          names = []
          for name, ct in Counter(derived_dataset_names).most_common(TOP_K):
            names.append(name)
            derived_dataset_names = names
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
  documents = load_documents(Path(PATH))
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
  with open("../data/atlas-dev-index.json", "w") as f:
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
