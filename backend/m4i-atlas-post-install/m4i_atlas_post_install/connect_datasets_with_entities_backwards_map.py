from pathlib import Path
import json
from typing import Any, MutableMapping
from collections import Counter
from m4i_atlas_post_install import (
    index_documents,
    load_documents
)

INPUT = "../data/atlas-dev.json"
OUTPUT = "../data/atlas-dev-index.json"

def get_derived_entities(dataset, atlas_dev_index: MutableMapping[str, Any]):
  derived_entity_guids = []
  attribute_guids = {}

  if dataset["derivedfieldguid"] is not None:
    for field_guid in dataset["derivedfieldguid"]:
      for attribute_guid in atlas_dev_index[field_guid]["deriveddataattributeguid"]:
        attribute = atlas_dev_index[attribute_guid]
        # Track the attribute by adding it to the attribute_guids dictionary
        attribute_guids[attribute_guid] = 0
        derived_entity_guids.extend(attribute["deriveddataentityguid"])

  entities_attribute_coverage = {}
  for entity_guid, ct in Counter(derived_entity_guids).most_common():
    entity = atlas_dev_index[entity_guid]
    coverage = 0
    # Mark the attributes as covered by this entity by setting attribute_guid to 1
    for attribute_guid in attribute_guids:
      if attribute_guid in entity["deriveddataattributeguid"] and attribute_guids[attribute_guid] != 1:
        attribute_guids[attribute_guid] = 1
        coverage += 1
    entities_attribute_coverage[entity_guid] = coverage

  # Return the entities whose attribute coverage is larger than zero
  derived_entity_guids = [entity_guid for entity_guid, coverage in entities_attribute_coverage.items() if coverage > 0]
  return derived_entity_guids


def update_index(atlas_dev_index: MutableMapping[str, Any], object_guid, key, value):
  existing_value = atlas_dev_index[object_guid][key]
  if existing_value is not None:
     atlas_dev_index[object_guid][key] = list(set(existing_value + value))
  else:
    atlas_dev_index[object_guid][key] = value

def backwards_map(documents, atlas_dev_index: MutableMapping[str, Any]):
  for document in documents:
      if document["typename"] == "m4i_dataset":
        derived_data_entity_guids = get_derived_entities(document, atlas_dev_index)
        derived_data_entity_names = [atlas_dev_index[guid]["name"] for guid in derived_data_entity_guids]
        print(f"Dataset {document['name']} has derived entities: {derived_data_entity_names}")

        # Update the dataset by adding its derived entities
        update_index(atlas_dev_index, document["guid"], "deriveddataentity", derived_data_entity_names)
        update_index(atlas_dev_index, document["guid"], "deriveddataentityguid", derived_data_entity_guids)

def main():

  # Load documents
  documents = load_documents(Path(INPUT))
  atlas_dev_index: MutableMapping[str, Any]= index_documents(documents)

  # Connect datasets with entities
  backwards_map(documents, atlas_dev_index)

  # Save updated index to file
  new_documents = list(atlas_dev_index.values())
  with open(OUTPUT, "w") as f:
    json.dump(new_documents, f, indent=4)

if __name__ == "__main__":
    main()
