#!/usr/bin/env python3

from collections.abc import Mapping
from typing import Any, MutableMapping, NewType, Tuple
from zipfile import ZipFile
import argparse
from pathlib import Path
from shutil import rmtree
import json

import dictdiffer


NON_ENTITY = [
    "atlas-typesdef.json",
    "atlas-export-order.json",
    "atlas-export-info.json",
]

TYPES_MAP = {
    "m4i_kafka_field": "m4i_field",
    "m4i_kafka_topic": "m4i_dataset",
    "m4i_visualization": "m4i_dataset",
    "m4i_dashboard": "m4i_dataset",
    "m4i_kafka_cluster": "m4i_system",
    "m4i_elastic_index": "m4i_dataset",
    "m4i_elastic_field": "m4i_field",
    "m4i_confluent_environment": "m4i_system",
    "m4i_elastic_cluster": "m4i_system",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", "-l", required=True, help="First export", type=Path)
    parser.add_argument("--right", "-r", required=True, help="Second export", type=Path)
    parser.add_argument(
        "--output", "-o", required=True, help="Output with patched types", type=Path
    )
    return parser.parse_args()


def extract(path: Path) -> Path:
    extract_path = Path("/tmp") / path.stem
    with ZipFile(path, "r") as zip:
        zip.extractall(path=extract_path)
    return extract_path


def extract_both(left: Path, right: Path) -> Tuple[Path, Path]:
    return extract(left), extract(right)


def cleanup(*temp_dirs: Path) -> None:
    for dir in temp_dirs:
        rmtree(dir)


def index_entities(path: Path) -> MutableMapping[str, MutableMapping[str, Any]]:
    index = {}
    for item in path.glob("*"):
        with open(item, "r") as json_file:
            index[str(item.name)] = json.load(json_file)
    return index


def index_both(
    left: Path, right: Path
) -> Tuple[
    MutableMapping[str, MutableMapping[str, Any]],
    MutableMapping[str, MutableMapping[str, Any]],
]:
    return index_entities(left), index_entities(right)


def get_added(diff: list[Tuple]) -> list[Tuple]:
    return [i for i in diff if i[0] == "add"]


def get_removed(diff: list[Tuple]) -> list[Tuple]:
    return [i for i in diff if i[0] == "remove"]


def get_changed(diff: list[Tuple]) -> list[Tuple]:
    return [i for i in diff if i[0] == "change"]


def get_deleted_entities(diff: list[Tuple]) -> list[Tuple]:
    removed = get_removed(diff)
    for item in removed:
        if item[1] == "":
            return item[2]
    return []


def filter_gov_quality(entities: list[Tuple]) -> list[Tuple]:
    return [
        i for i in entities if i[1]["entity"]["typeName"] in ["m4i_gov_data_quality"]
    ]


def update_types(entity: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    for key, value in TYPES_MAP.items():
        content = json.dumps(entity)
        content = content.replace(key, value)
        entity = json.loads(content)
    return entity


def update_all_entities(entities: list[Tuple]) -> list[Tuple]:
    for entity in entities:
        entity[1]["entity"] = update_types(entity[1]["entity"])
    return entities


def create_patch(entities: list[Tuple]) -> list[Tuple]:
    return [("add", "", entities)]


def update_index(
    index: MutableMapping[str, Any], patch: list[Tuple]
) -> MutableMapping[str, Any]:
    return dictdiffer.patch(patch, index)


def filter_duplicates(index: MutableMapping[str, Any]) -> None:
    duplicated = []
    unique_names = []
    for key, value in index.items():
        if key not in NON_ENTITY:
            qualified_name = value["entity"]["attributes"].get("qualifiedName")
            if not qualified_name:
                continue
            if qualified_name not in unique_names:
                unique_names.append(value["entity"]["attributes"]["qualifiedName"])
            else:
                duplicated.append(key)
    for key in duplicated:
        del index[key]


def dump_index(index: Mapping[str, Any], output_path: Path) -> Path:
    temp_path = Path("/tmp") / output_path.stem
    temp_path.mkdir(exist_ok=True)
    with ZipFile(output_path, "w") as output_file:
        for key, value in index.items():
            with open(temp_path / key, "w") as json_file:
                json.dump(value, json_file, indent=4)
            output_file.write(temp_path / key, arcname=key)

    return temp_path


def update_export_order(index: MutableMapping[str, Any]) -> None:
    new_export_order = []
    for key in index.keys():
        if key not in NON_ENTITY:
            new_export_order.append(Path(key).stem)
    index["atlas-export-order.json"] = new_export_order


def update_metrics(index: MutableMapping[str, Any]) -> None:
    metrics = {}
    total_entities = 0
    metrics["duration"] = index["atlas-export-info.json"]["metrics"]["duration"]
    for key, value in index.items():
        if key not in NON_ENTITY:
            entity_type = value["entity"]["typeName"]
            metrics_field = f"entity:{entity_type}"
            if metrics.get(metrics_field):
                metrics[metrics_field] += 1
            else:
                metrics[metrics_field] = 1
            total_entities += 1
    metrics["entity:withExtInfo"] = total_entities
    index["atlas-export-info.json"]["metrics"] = metrics


def drop_non_entities(entities: MutableMapping[str, Any]) -> None:
    for non_entity in NON_ENTITY:
        del entities[non_entity]


def main() -> None:
    args = parse_args()
    left, right = extract_both(args.left, args.right)
    left_index, right_index = index_both(left, right)
    diff = list(dictdiffer.diff(left_index, right_index, ignore=set(NON_ENTITY)))
    deleted_entities = get_deleted_entities(diff)
    filtered = filter_gov_quality(deleted_entities)
    update_all_entities(filtered)
    patched = update_index(right_index, create_patch(filtered))
    filter_duplicates(patched)
    update_metrics(patched)
    update_export_order(patched)
    temp_path = dump_index(patched, args.output)
    cleanup(left, right, temp_path)


if __name__ == "__main__":
    main()
