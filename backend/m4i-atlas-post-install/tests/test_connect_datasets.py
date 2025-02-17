from m4i_atlas_post_install import (
  connect_entities_with_datasets as connect,
  load_documents,
  index_documents,
)
from pathlib import Path
from typing import Any, MutableMapping

def test_get_derived_datasets():

  # Read test data
  # Test data has one entity linked with three fields
  # Dataset one covers fields 1,2 and 3, dataset two covers fields 2 and 3, dataset three covers fields 3 and 4
  documents = load_documents(Path("tests/test_data.json"))
  atlas_dev_index : MutableMapping[str, Any] = index_documents(documents)

  # Call the connect method
  connect.connect_entities_with_datasets(documents, atlas_dev_index)

  # Check if the dev_index has been updated with the right values
  # Dataset one and three should be linked to the entity
  assert sorted(atlas_dev_index["entity-guid"]["deriveddatasetguid"]) == sorted(["dataset-one-guid", "dataset-three-guid"])
  assert sorted(atlas_dev_index["entity-guid"]["deriveddataset"]) == sorted(["dataset_one", "dataset_three"])
