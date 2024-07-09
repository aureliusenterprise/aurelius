import argparse
from pathlib import Path
from typing import Any, List, MutableMapping

from elastic_enterprise_search import AppSearch
from m4i_atlas_post_install import get_enterprise_search_key, index_all_documents
from m4i_atlas_post_install.documents_utils import index_documents, load_documents

DIMENSIONS = ["accuracy", "completeness", "timeliness", "validity", "uniqueness"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "-a", required=True, help="App Search url", type=str)
    parser.add_argument(
        "--username", "-u", default="elastic", help="ES username", type=str
    )
    parser.add_argument("--password", "-p", required=True, help="ES password", type=str)
    parser.add_argument(
        "--atlas-dev",
        default=Path("data/atlas-dev.json"),
        type=Path,
        help="Path to atlas-dev JSON dump",
    )
    parser.add_argument(
        "--quality",
        default=Path("data/atlas-dev-quality.json"),
        type=Path,
        help="Path to atlas-dev-quality JSON dump",
    )
    return parser.parse_args()


def zero_everything(atlas_dev_index: MutableMapping[str, Any]):
    for document in atlas_dev_index.values():
        for dimension in DIMENSIONS:
            document[f"dqscoresum_{dimension}"] = 0.0
            document[f"dqscorecnt_{dimension}"] = 0.0
            document[f"dqscore_{dimension}"] = 0.0
            document[f"qualityguid_{dimension}"] = []
        document["dqscoresum_overall"] = 0.0
        document["dqscorecnt_overall"] = 0.0
        document["dqscore_overall"] = 0.0


def update_quality_field(
    quality_document: MutableMapping[str, Any],
    entity_document: MutableMapping[str, Any],
):
    dimension = quality_document["dataqualityruledimension"].lower()
    entity_document[f"dqscoresum_{dimension}"] += quality_document["dqscore"]
    entity_document[f"dqscorecnt_{dimension}"] += 1
    entity_document[f"dqscore_{dimension}"] = (
        entity_document[f"dqscoresum_{dimension}"]
        / entity_document[f"dqscorecnt_{dimension}"]
    )
    entity_document[f"qualityguid_{dimension}"].append(quality_document["qualityguid"])


def update_quality_fields(
    quality_documents: List[MutableMapping[str, Any]],
    atlas_dev_index: MutableMapping[str, Any],
):
    for quality_document in quality_documents:
        entity_document = atlas_dev_index[quality_document["fieldguid"]]
        update_quality_field(quality_document, entity_document)


def update_quality_scores(
    downstream_document: MutableMapping[str, Any],
    upstream_document: MutableMapping[str, Any],
    dimension: str,
):
    upstream_document[f"dqscoresum_{dimension}"] += downstream_document[
        f"dqscoresum_{dimension}"
    ]
    upstream_document[f"dqscorecnt_{dimension}"] += downstream_document[
        f"dqscorecnt_{dimension}"
    ]

    if upstream_document[f"dqscorecnt_{dimension}"] == 0:
        return

    upstream_document[f"dqscore_{dimension}"] = (
        upstream_document[f"dqscoresum_{dimension}"]
        / upstream_document[f"dqscorecnt_{dimension}"]
    )


def update_quality_scores_per_dimension(
    downstream_document: MutableMapping[str, Any],
    upstream_document: MutableMapping[str, Any],
):
    for dimension in DIMENSIONS:
        update_quality_scores(
            downstream_document=downstream_document,
            upstream_document=upstream_document,
            dimension=dimension,
        )


def update_quality_attributes(
    atlas_dev_index: MutableMapping[str, Any],
):
    for document in atlas_dev_index.values():
        if document["typename"] == "m4i_field":
            for attribute_guid in document["deriveddataattributeguid"]:
                update_quality_scores_per_dimension(
                    downstream_document=document,
                    upstream_document=atlas_dev_index[attribute_guid],
                )


def propagate_quality(
    atlas_dev_index: MutableMapping[str, Any],
):
    for document in atlas_dev_index.values():
        if document["typename"] in ["m4i_data_attribute", "m4i_field"]:
            downstream_document = document
            for breadcrumb_guid in document["breadcrumbguid"]:
                upstream_document = atlas_dev_index[breadcrumb_guid]
                update_quality_scores_per_dimension(
                    downstream_document=downstream_document,
                    upstream_document=upstream_document,
                )


def update_overall_scores(atlas_dev_index: MutableMapping[str, Any]):
    for document in atlas_dev_index.values():
        update_overall_score(document)


def update_overall_score(document: MutableMapping[str, Any]):
    for dimension in DIMENSIONS:
        document["dqscoresum_overall"] += document[f"dqscoresum_{dimension}"]
        document["dqscorecnt_overall"] += document[f"dqscorecnt_{dimension}"]
    if document["dqscorecnt_overall"] == 0:
        return

    document["dqscore_overall"] = (
        document["dqscoresum_overall"] / document["dqscorecnt_overall"]
    )


def main():
    args = parse_args()
    app_search_api_key = get_enterprise_search_key(
        args.url, args.username, args.password
    )

    app_search_client = AppSearch(args.url, bearer_auth=app_search_api_key)

    atlas_dev_documents = load_documents(args.atlas_dev)
    quality_documents = load_documents(args.quality)
    atlas_dev_index = index_documents(atlas_dev_documents)
    zero_everything(atlas_dev_index)
    update_quality_fields(quality_documents, atlas_dev_index)
    update_quality_attributes(atlas_dev_index)
    propagate_quality(atlas_dev_index)
    update_overall_scores(atlas_dev_index)
    index_all_documents(
        engine_name="atlas-dev",
        app_search_client=app_search_client,
        documents=list(atlas_dev_index.values()),
    )
    print("Updated atlas-dev")
    index_all_documents(
        engine_name="atlas-dev-quality",
        app_search_client=app_search_client,
        documents=quality_documents,
    )
    print("Updated atlas-dev-quality")


if __name__ == "__main__":
    main()
