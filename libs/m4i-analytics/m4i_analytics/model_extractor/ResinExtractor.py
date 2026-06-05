"""
Resin Extractor module for extracting data from Resin models.

Created on Thu Aug 16 12:20:28 2018
@author: andre
"""

import numpy as np
import pandas as pd
from resin import Resin

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType,
    RelationshipType,
)
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import ArchimateModel

# from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.visualisations.GraphPlotter import Layout
from m4i_analytics.model_extractor.ExtractorLanguagePrimitives import (
    ExtractorLanguagePrimitives,
)

# from datetime import datetime
from m4i_analytics.model_extractor.model.Extractor import ExtractionResult, Extractor


class ResinExtractor(Extractor):
    username = None
    password = None

    def __init__(
        self,
        branch_name="Resin",
        username=None,
        password=None,
        log_file_path=None,
        log_file_format=(
            "%(asctime)s - %(name)s -%(relativeCreated)6d %(threadName)s - %(levelname)s - %(message)s"
        ),
    ):
        super().__init__(
            branch_name=branch_name,
            log_file_path=log_file_path,
            log_file_format=log_file_format,
        )
        self.username = username
        self.password = password

    # END __init__

    def extract(self, data_only=False):
        model = ArchimateModel("resin_model", defaultAttributeMapping=True)

        script_name = "resin model extractor"

        views = []
        element_metadata = []
        nodes = []
        # connections = []

        resin = Resin()
        credentials = {"username": self.username, "password": self.password}
        resin.auth.login(**credentials)

        applications_ = resin.models.application.get_all()
        applications = pd.DataFrame(applications_)
        applications["type"] = "application"

        ids = [
            {
                "prefix": "resin_app_",
                "id_key": "id",
                "concept_name_prefix": "",
                "concept_name_key": "app_name",
                "concept_label_prefix": "",
                "concept_label_key": "app_name",
                "concept_type": ElementType.APPLICATION_COMPONENT,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "id_prefix", "value": "resin_app_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            },
            {
                "prefix": "resin_git_",
                "id_key": "id",
                "concept_name_prefix": "GIT ",
                "concept_name_key": "git_repository",
                "concept_label_prefix": "GIT ",
                "concept_label_key": "git_repository",
                "concept_type": ElementType.DATA_OBJECT,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "id_prefix", "value": "resin_git_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            },
            {
                "prefix": "resin_dev_type_",
                "id_key": "id",
                "concept_name_prefix": "",
                "concept_name_key": "device_type",
                "concept_label_prefix": "",
                "concept_label_key": "device_type",
                "concept_type": ElementType.DEVICE,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "id_prefix", "value": "resin_dev_type_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            },
        ]
        res = ExtractorLanguagePrimitives.parse_concept(applications, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])

        rels_all = []
        for _index, app in applications.iterrows():
            app_id = app["id"]
            if app["commit"] is not None:
                rels_ = resin.models.release.get_all_by_application(app_id)
                rels_all.extend(rels_)
        rels = pd.DataFrame(rels_all)

        devices_ = resin.models.device.get_all()
        devices = pd.DataFrame(devices_)
        devices["app_id"] = devices["belongs_to__application"].apply(lambda x: x["__id"])
        devices = devices.merge(applications, how="left", left_on="app_id", right_on="id")
        devices["app_name_device_name"] = devices.apply(
            lambda x: "{} - {}".format(x["app_name"], x["device_name"]), axis=1
        )
        devices["os_version_device_name"] = devices.apply(
            lambda x: "{} - {}".format(x["os_version"], x["device_name"]), axis=1
        )
        devices["type"] = "devices"

        ids = [
            {
                "prefix": "resin_dev_",
                "id_key": "device_name",
                "concept_name_prefix": "",
                "concept_name_key": "device_name",
                "concept_label_prefix": "",
                "concept_label_key": "device_name",
                "concept_type": ElementType.DEVICE,
                "mapping": [
                    {"key": "original_id", "value": "id_x"},
                    {"key": "actor", "value": "actor_x"},
                    {"key": "created_at", "value": "created_at"},
                    {"key": "ip_address", "value": "ip_address"},
                    {"key": "is_active", "value": "is_active"},
                    {"key": "is_connected_to_vpn", "value": "is_connected_to_vpn"},
                    {"key": "is_online", "value": "is_online"},
                    {
                        "key": "last_connectivity_event",
                        "value": "last_connectivity_event",
                    },
                    {"key": "last_vpn_event", "value": "last_vpn_event"},
                    {"key": "latitude", "value": "latitude"},
                    {"key": "local_id", "value": "local_id"},
                    {"key": "location", "value": "location"},
                    {"key": "longitude", "value": "longitude"},
                    {"key": "note", "value": "note"},
                    {"key": "os_variant", "value": "os_variant"},
                    {"key": "status", "value": "status"},
                    {"key": "public_address", "value": "public_address"},
                    {"key": "supervisor_version", "value": "supervisor_version"},
                    {"key": "uuid", "value": "uuid"},
                    {"key": "vpn_address", "value": "vpn_address"},
                    {"key": "id_prefix", "value": "resin_dev_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            },
            {
                "prefix": "resin_dev_app_",
                "id_key": "device_name",
                "concept_name_prefix": "",
                "concept_name_key": "app_name_device_name",
                "concept_label_prefix": "",
                "concept_label_key": "app_name_device_name",
                "concept_type": ElementType.APPLICATION_COMPONENT,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "id_prefix", "value": "resin_dev_app_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            },
            {
                "prefix": "resin_dev_serv_",
                "id_key": "device_name",
                "concept_name_prefix": "",
                "concept_name_key": "os_version_device_name",
                "concept_label_prefix": "",
                "concept_label_key": "os_version_device_name",
                "concept_type": ElementType.SYSTEM_SOFTWARE,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "id_prefix", "value": "resin_dev_serv_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            },
        ]
        res = ExtractorLanguagePrimitives.parse_concept(devices, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])

        com = list(np.unique(devices[np.logical_not(devices.is_on__commit.isnull())].is_on__commit))

        rels_rel = rels[rels.created_at >= rels[rels.commit.isin(com)].created_at.min()].copy()
        rels_rel["app_id"] = rels_rel.belongs_to__application.apply(lambda x: x["__id"])

        ids = [
            {
                "prefix": "resin_commit_",
                "id_key": "commit",
                "concept_name_prefix": "commit ",
                "concept_name_key": "commit_short",
                "concept_label_prefix": "commit ",
                "concept_label_key": "commit_short",
                "concept_type": ElementType.PLATEAU,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "commit", "value": "commit"},
                    {"key": "committed_on", "value": "created_at"},
                    {"key": "id_prefix", "value": "resin_commit_"},
                    {"key": "resin_concept_type", "value": "type"},
                ],
            }
        ]

        rels_rel["commit_short"] = rels_rel["commit"].apply(lambda x: x[:6])
        res = ExtractorLanguagePrimitives.parse_concept(rels_rel, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])
        nodes_df = pd.DataFrame(nodes)

        model.nodes = nodes_df

        edges = []

        # edges related to applications
        ids = [
            {
                "prefix": "resin_git_app_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.SERVING,
                "source_prefix": "resin_git_",
                "source_id_key": "id",
                "target_prefix": "resin_app_",
                "target_id_key": "id",
                "mapping": [],
            },
            {
                "prefix": "resin_app_release_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.ASSOCIATION,
                "source_prefix": "resin_commit_",
                "source_id_key": "commit",
                "target_prefix": "resin_app_",
                "target_id_key": "id",
                "mapping": [],
            },
        ]
        res = ExtractorLanguagePrimitives.parse_relationship(applications, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        edges.extend(res["edges"])

        # edges related to releases
        rels_rel_base = rels_rel[["app_id", "commit", "created_at"]].sort_values(
            by=["app_id", "created_at"], ascending=False
        )
        if len(rels_rel_base) > 1:
            rels_rel_edge = rels_rel_base[0 : len(rels_rel_base) - 1].copy()
            rels_rel_edge[["src_app_id", "src_commit"]] = rels_rel_base[1 : len(rels_rel_base)][
                ["app_id", "commit"]
            ].copy()
            rels_rel_edge["id"] = rels_rel_edge.apply(
                lambda x: "{}-{}".format(x["src_commit"], x["commit"]), axis=1
            )
            rels_rel_edge = rels_rel_edge[
                rels_rel_edge.apply(lambda x: x["app_id"] == x["src_app_id"], axis=1)
            ]
            if len(rels_rel_edge) > 0:
                ids = [
                    {
                        "prefix": "resin_commit_commit_",
                        "id_key": "id",
                        "relationship_name_prefix": "",
                        "relationship_name_key": "",
                        "relationship_label_prefix": "",
                        "relationship_label_key": "",
                        "relationship_type": RelationshipType.TRIGGERING,
                        "source_prefix": "resin_commit_",
                        "source_id_key": "src_commit",
                        "target_prefix": "resin_commit_",
                        "target_id_key": "commit",
                        "mapping": [],
                    }
                ]
                res = ExtractorLanguagePrimitives.parse_relationship(
                    rels_rel_edge, model, ids, script_name, data_only
                )
                element_metadata.extend(res["metadata"])
                edges.extend(res["edges"])

        # edges related to devices
        ids = [
            {
                "prefix": "resin_commit_dev_",
                "id_key": "id_x",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.AGGREGATION,
                "source_prefix": "resin_commit_",
                "source_id_key": "commit",
                "target_prefix": "resin_dev_app_",
                "target_id_key": "device_name",
                "mapping": [],
            },
            {
                "prefix": "resin_class_dev_",
                "id_key": "id_x",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.AGGREGATION,
                "source_prefix": "resin_dev_type_",
                "source_id_key": "app_id",
                "target_prefix": "resin_dev_",
                "target_id_key": "device_name",
                "mapping": [],
            },
            {
                "prefix": "resin_dev_dev_serv_",
                "id_key": "id_x",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.SERVING,
                "source_prefix": "resin_dev_",
                "source_id_key": "device_name",
                "target_prefix": "resin_dev_serv_",
                "target_id_key": "device_name",
                "mapping": [],
            },
            {
                "prefix": "resin_dev_serv_dev_app_",
                "id_key": "id_x",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.SERVING,
                "source_prefix": "resin_dev_serv_",
                "source_id_key": "device_name",
                "target_prefix": "resin_dev_app_",
                "target_id_key": "device_name",
                "mapping": [],
            },
        ]
        res = ExtractorLanguagePrimitives.parse_relationship(devices, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        edges.extend(res["edges"])

        edges_df = pd.DataFrame(edges)

        model.edges = edges_df

        # create views

        # views will be organized in folders, while the concepts and relationships
        # are not. Therefore, it is necessary to call the model.organize to add
        # the concepts and relationships to the model Organizations and then
        # create the views. Otherwise, the organization of the view will be overwritten.
        model.organize()

        # overview view of all applications
        views = []

        ids = [
            {
                "id_type": "static",
                "id_value": "view_resin_overview",
                "view_name_type": "static",
                "view_name_value": "overview",
                "view_path": [{"type": "static", "value": "resin"}],
                "view_nodes": [
                    {"id_prefix": "resin_app_", "id_key": "id"},
                    {"id_prefix": "resin_git_", "id_key": "id"},
                ],
                "view_edges": [{"id_prefix": "resin_git_app_", "id_key": "id"}],
                "view_layout": Layout.HIERARCHICAL,
            }
        ]
        #      data = applications
        res = ExtractorLanguagePrimitives.parse_view(applications, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        views.extend(res["views"])

        # overview view perapplication
        ids = [
            {
                "id_type": "dynamic",
                "id_prefix": "resin_overview_",
                "id_key": "app_name",
                "view_name_type": "dynamic",
                "view_name_prefix": "version history ",
                "view_name_key": "app_name",
                "view_path": [
                    {"type": "static", "value": "resin"},
                    {"type": "dynamic", "prefix": "", "value": "app_name"},
                ],
                "view_nodes": [
                    {"id_prefix": "resin_app_", "id_key": "id_y"},
                    {"id_prefix": "resin_dev_app_", "id_key": "device_name"},
                    {"id_prefix": "resin_commit_", "id_key": "commit"},
                ],
                "view_edges": [
                    {"id_prefix": "resin_app_release_", "id_key": "id_y"},
                    {"id_prefix": "resin_commit_dev_", "id_key": "id_x"},
                ],
                "view_layout": Layout.HIERARCHICAL,
            }
        ]
        res = ExtractorLanguagePrimitives.parse_view(devices, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        views.extend(res["views"])

        # default_coor = [{"@x" : 300, "@y" : 336},
        #            {"@x" : 541, "@y" : 338},
        #            {"@x" : 300,"@y" : 132},
        #            {"@x" : 300,"@y" : 252},
        #            {"@x" : 541,"@y" : 102},
        #            {"@x" : 539,"@y" : 177},
        #            {"@x" : 774,"@y" : 148},
        #            {"@x" : 96,"@y" : 132}]
        # devices:
        #   concepts:
        #       device: 'prefix':'resin_dev_','id_key':'id_x'
        #       application component: 'prefix':'resin_dev_app_','id_key':'id_x'
        #       system_software: 'prefix':'resin_dev_serv_','id_key':'id_x'
        #       plateau: 'prefix':'resin_commit_','id_key':'is_on__commit'
        #   edges:
        #       'prefix':'resin_commit_dev_','id_key':'id_x'
        #       'prefix':'resin_class_dev_','id_key':'id_x'
        #       'prefix':'resin_dev_dev_serv_','id_key':'id_x'
        #       'prefix':'resin_dev_serv_dev_app_','id_key':'id_x'
        ids = [
            {
                "id_type": "dynamic",
                "id_prefix": "resin_overview_",
                "id_key": "id_x",
                "view_name_type": "dynamic",
                "view_name_prefix": "",
                "view_name_key": "device_name",
                "view_path": [
                    {"type": "static", "value": "resin"},
                    {"type": "dynamic", "prefix": "", "value": "app_name"},
                ],
                "view_nodes": [
                    {
                        "id_prefix": "resin_dev_",
                        "id_key": "device_name",
                        "x": 300,
                        "y": 336,
                    },
                    {
                        "id_prefix": "resin_dev_app_",
                        "id_key": "device_name",
                        "x": 300,
                        "y": 132,
                    },
                    {
                        "id_prefix": "resin_dev_serv_",
                        "id_key": "device_name",
                        "x": 300,
                        "y": 252,
                    },
                    {
                        "id_prefix": "resin_commit_",
                        "id_key": "is_on__commit",
                        "x": 96,
                        "y": 132,
                    },
                    {
                        "id_prefix": "resin_dev_type_",
                        "id_key": "app_id",
                        "x": 541,
                        "y": 338,
                    },
                ],
                "view_edges": [
                    {"id_prefix": "resin_commit_dev_", "id_key": "id_x"},
                    {"id_prefix": "resin_class_dev_", "id_key": "id_x"},
                    {"id_prefix": "resin_dev_dev_serv_", "id_key": "id_x"},
                    {"id_prefix": "resin_dev_serv_dev_app_", "id_key": "id_x"},
                ],
                "view_layout": Layout.MANUAL,
            }
        ]
        res = ExtractorLanguagePrimitives.parse_view(devices, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        views.extend(res["views"])

        return ExtractionResult(model, element_metadata, self.branch_name)

    # END extract


# END ResinExtractor
