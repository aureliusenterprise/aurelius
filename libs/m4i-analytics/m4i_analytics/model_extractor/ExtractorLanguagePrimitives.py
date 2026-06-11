"""
Created on Mon Aug 20 21:41:19 2018

@author: andre
"""

import math
import numbers
from abc import ABCMeta
from itertools import chain

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType


class AttributeMapping(dict):
    """
    This class provides a structure to define an attribute mapping for
    model elements (i.e. concepts, relations or views).
    """

    def __init__(self, key, value):
        """
        :param str key: the name of the attribute
        :param str value: the key of the attribute in the source data
        """

        self["key"] = key
        self["value"] = value

    # END __init__


# END AttributeMapping


class ConceptDefinition(dict):
    __metaclass__ = ABCMeta

    def __init__(self, id, id_key, id_prefix="", mapping=None):
        """
        :param str id_key: the key to the concept id
        :param str id_prefix: *Optional*. A prefix for the concept id.
            Defaults to an empty string.
        :param list of AttributeMapping mapping: *Optional*. The set of
            attributes that should be attached for every concept.
            Defaults to an empty list.
        """

        if mapping is None:
            mapping = []
        self["id"] = id
        self["id_prefix"] = id_prefix if id_prefix else ""
        self["id_key"] = id_key
        self["mapping"] = mapping if mapping else []

    # END __init__


# END ConceptDefinition


class ElementDefinition(ConceptDefinition):
    """
    This class provides a structure to define a model element mapping for the extractor primitives.
    """

    def __init__(
        self,
        id,
        id_key,
        concept_type,
        id_prefix="",
        concept_name_prefix="",
        concept_name_key="",
        concept_label_prefix="",
        concept_label_key="",
        mapping=None,
        **kwargs,
    ):
        """
        :param str id_key: the key to the element id
        :param ElementType concept_type: the type of the elements that will
            be created
        :param str id_prefix: *Optional*. A prefix for the element id.
        :param str concept_name_prefix: *Optional*. A prefix for the element name.
        :param str concept_name_key: *Optional*. The key to the element name.
            Set this if you want to assign a name to the concepts. Defaults
            to an empty string.
        :param str concept_label_prefix: *Optional*. A prefix for the element label.
        :param str concept_label_key: *Optional*. The key to the element label.
            Set this if you want to assign a label to the concepts. Defaults
            to an empty string.
        :param list of AttributeMapping mapping: *Optional*. The set of
            attributes that will be attached for every element.
            Defaults to an empty list.
        """

        if mapping is None:
            mapping = []
        super().__init__(id, id_key, id_prefix, mapping)

        self["concept_name_prefix"] = concept_name_prefix if concept_name_prefix else ""
        self["concept_name_key"] = concept_name_key
        self["concept_label_prefix"] = concept_label_prefix if concept_label_prefix else ""
        self["concept_label_key"] = concept_label_key
        self["concept_type"] = (
            concept_type if not isinstance(concept_type, str) else ElementType.getElementByTag(concept_type)
        )

    # END __init__


# END ElementDefinition


class RelationshipDefinition(ConceptDefinition):
    """
    This class provides a structure to define a model relationship for the extractor primitives.
    """

    def __init__(
        self,
        id,
        id_key,
        source_id_key,
        target_id_key,
        relationship_type,
        id_prefix="",
        source_prefix="",
        target_prefix="",
        relationship_name_prefix="",
        relationship_label_prefix="",
        relationship_name_key="",
        relationship_label_key="",
        mapping=None,
        **kwargs,
    ):
        """
        :param str id_key: the key to the relationship id
        :param str source_id_key: the id of the source
        :param str target_id_key: the id of the target
        :param str relationship_type: the type of relationships that will be
            created
        :param str id_prefix: *Optional*. A prefix for the relationship id.
            Defaults to an empty string.
        :param str source_prefix: *Optional*. The prefix for the id of the
            source. Defaults to an empty string.
        :param str target_prefix: *Optional*. The prefix for the id of the
            target. Defaults to an empty string.
        :param str relationship_name_prefix: *Optional*. A prefix for the
            relationship name. Defaults to an empty string.
        :param str relationship_label_prefix: *Optional*. A prefix for the
            relationship label. Defaults to an empty string.
        :param str relationship_name_key: *Optional*. The key to the
            relationship name. Defaults to an empty string.
        :param str relationship_label_key: *Optional*. The key to the
            relationship label. Defaults to an empty string.
        :param list of AttributeMapping mapping: *Optional*. The set of
            attributes that will be attached for every relationship.
            Defaults to an empty list.
        """

        if mapping is None:
            mapping = []
        super().__init__(id, id_key, id_prefix, mapping)

        self["relationship_name_prefix"] = relationship_name_prefix if relationship_name_prefix else ""
        self["relationship_name_key"] = relationship_name_key
        self["relationship_label_prefix"] = relationship_label_prefix if relationship_label_prefix else ""
        self["relationship_label_key"] = relationship_label_key
        self["relationship_type"] = (
            relationship_type
            if not isinstance(relationship_type, str)
            else RelationshipType.getRelationshipByShorthand(relationship_type)
        )
        self["source_prefix"] = source_prefix if source_prefix else ""
        self["source_id_key"] = source_id_key
        self["target_prefix"] = target_prefix if target_prefix else ""
        self["target_id_key"] = target_id_key

    # END __init__


# END RelationshipDefinition


class ViewPathMapping(dict):
    """
    This class provides a structure to define the path to a view in the model organization.
    """

    def __init__(self, value, type_="static"):
        """
        :param str value: The name of the folder in the organization, or the
            key to the value in the dataset.
        :param 'static' | 'dynamic' type_: *Optional*. Whether to use the value
            in the path directly, or to use the value as a lookup reference.
            Defaults to 'static'.
        """

        self["type"] = type_
        self["value"] = value

    # END __init__


# END ViewPathMapping


class ViewDefinition(ConceptDefinition):
    """
    This class provides a structure to define a model view for the extractor primitives.
    """

    def __init__(
        self,
        id,
        view_layout,
        id_type="dynamic",
        view_name_type="dynamic",
        view_nodes=None,
        view_edges=None,
        id_key="",
        id_prefix="",
        id_value="",
        view_name_key="",
        view_name_prefix="",
        view_name_value="",
        view_path=None,
        mapping=None,
        **kwargs,
    ):
        """
        :param str id_key: the name of the views (if id_type = 'static'), or
            the key to the view id (if id_type ='dynamic').
        :param str view_name_key: the name of the view (if view_name_type =
            'static'), or the key to the view name (if view_name_type =
            'dynamic').
        :param Layout view_layout: the layout to use for the view
        :param 'static' | 'dynamic' id_type: *Optional*. Whether the positions
            of the elements in the views are preset or calculated.
            Defaults to 'dynamic'.
        :param 'static' | 'dynamic' view_name_type: *Optional*. Whether the
            titles of the views is preset or calculated. Defaults to 'dynamic'.
        :param str view_nodes: *Optional*. The nodes to include in the views.
            Defaults to an empty list.
        :param str view_edges: *Optional*. The edges to include in the views.
            Defaults to an empty list.
        :param str id_prefix: *Optional*. A prefix for the view id. Defaults
            to an empty string.
        :param str view_name_prefix: *Optional*. A prefix for the view name.
            Defaults to an empty string.
        :param list of ViewPathMapping view_path: *Optional*. The path of the
            created views in the organization of the model. Defaults to an
            empty list.
        :param list of AttributeMapping mapping: *Optional*. The set of
            attributes that will be attached for every view. Defaults to an
            empty list.
        """

        if mapping is None:
            mapping = []
        if view_path is None:
            view_path = []
        if view_edges is None:
            view_edges = []
        if view_nodes is None:
            view_nodes = []
        super().__init__(id, id_key, id_prefix, mapping)

        self["id_type"] = id_type
        self["id_value"] = id_value
        self["view_name_type"] = view_name_type
        self["view_name_key"] = view_name_key
        self["view_nodes"] = view_nodes if view_nodes else []
        self["view_edges"] = view_edges if view_edges else []
        self["view_layout"] = view_layout
        self["view_name_prefix"] = view_name_prefix if view_name_prefix else ""
        self["view_name_value"] = view_name_value if view_name_value else ""
        self["view_path"] = view_path
        self["mapping"] = mapping

    # END __init__


# END ViewDefinition


class ExtractorLanguagePrimitives:
    """
    This class provides methods to create various methods to create model elements
    based on a mapping between a data source and concept types. The mapping is based
    on a common definition language. The components of the definition language are
    also provided in this module.
    """

    @staticmethod
    def _parse_concept_data(row, definition, script_name="model_extractor"):
        content = {
            "created_by": script_name,
            "m4i_id_prefix": definition["id_prefix"],
            "m4i_original_id": str(row[definition["id_key"]]),
        }

        # This loop maps all attributes from the definition mapping
        for map_ in definition["mapping"]:
            if map_["value"] in row and (
                row[map_["value"]] is not None and row[map_["value"]] == row[map_["value"]]
            ):
                content[map_["key"]] = row[map_["value"]]
        # END LOOP

        return {"id": "{}{}".format(definition["id_prefix"], row[definition["id_key"]]), "data": content}

    # END _parse_concept_data

    @staticmethod
    def _parse_concept_node(row, definition):
        return {
            "id": "{}{}".format(definition["id_prefix"], row[definition["id_key"]]),
            "type": definition["concept_type"],
            "name": "{}{}".format(definition["concept_name_prefix"], row[definition["concept_name_key"]])
            if definition["concept_name_key"] and definition["concept_name_key"] in row
            else "",
            "label": "{}{}".format(definition["concept_label_prefix"], row[definition["concept_label_key"]])
            if definition["concept_label_key"] and definition["concept_label_key"] in row
            else "",
        }

    # END _parse_concept_node

    @staticmethod
    def _parse_concept_definition(data, definition, script_name="model extractor", data_only=False):
        # Remove any duplicates in the dataset based on the ID in the definition
        # (if any). Only the first occurrence of any ID is retained.
        if definition["id_key"] in data.columns:
            deduplicated_data = data.drop_duplicates(subset=definition["id_key"])
            deduplicated_data = deduplicated_data[
                deduplicated_data[definition["id_key"]] == deduplicated_data[definition["id_key"]]
            ]
            return {
                "metadata": (
                    ExtractorLanguagePrimitives._parse_concept_data(row, definition, script_name)
                    for index, row in deduplicated_data.iterrows()
                ),
                "nodes": (
                    ExtractorLanguagePrimitives._parse_concept_node(row, definition)
                    for index, row in deduplicated_data.iterrows()
                    if not data_only
                ),
            }
        else:
            return {"metadata": [], "nodes": []}

    # END _parse_concept_definition

    @staticmethod
    def parse_concept(data, definitions, script_name="model extractor", data_only=False):
        """
        Use the provided definitions to generate nodes from the given dataset

        :returns: A dictionary containing the nodes and metadata generated.
        :rtype: {
            'nodes': iterable,
            'metadata': iterable
        }

        :param pandas.DataFrame data: The dataset from which to generate
            the nodes.
        :param ElementDefinition | list of ElementDefinition definitions:
            The definitions that declare the nodes to generate. You can also
            pass a single definition.
        :param str script_name: *Optional*. The name of the calling script for
            provenance. Defaults to 'model extractor'.
        :param boolean data_only: *Optional*. Whether or not the elements
            should be generated in addition to the data associated with them.
            Defaults to False.
        """

        # You can also pass a single definition into this function
        _definitions = iter(list(definitions))
        nodes = iter([])
        metadata = iter([])

        for definition in _definitions:
            parsed_definition = ExtractorLanguagePrimitives._parse_concept_definition(
                data, definition, script_name, data_only
            )
            nodes = chain(nodes, parsed_definition["nodes"])
            metadata = chain(metadata, parsed_definition["metadata"])
        # END LOOP

        return {"nodes": nodes, "metadata": metadata}

    # END parse_concept

    @staticmethod
    def _parse_relationship_data(row, definition, script_name):
        content = {
            "created_by": script_name,
            "m4i_id_prefix": definition["id_prefix"],
            "m4i_original_id": str(row[definition["id_key"]]),
        }

        for map_ in definition["mapping"]:
            if row[map_["value"]] is not None and row[map_["value"]] == row[map_["value"]]:
                content[map_["key"]] = row[map_["value"]]
        # END LOOP

        return {"id": "{}{}".format(definition["id_prefix"], row[definition["id_key"]]), "data": content}

    # END _parse_relationship_data

    @staticmethod
    def _parse_relationship_edge(row, definition):
        return {
            "id": "{}{}".format(definition["id_prefix"], row[definition["id_key"]]),
            "type": definition["relationship_type"],
            "source": "{}{}".format(definition["source_prefix"], row[definition["source_id_key"]]),
            "target": "{}{}".format(definition["target_prefix"], row[definition["target_id_key"]]),
            "name": "{}{}".format(
                definition["relationship_name_prefix"], row[definition["relationship_name_key"]]
            )
            if definition["relationship_name_key"] in row
            else "",
            "label": "{}{}".format(
                definition["relationship_label_prefix"], row[definition["relationship_label_key"]]
            )
            if definition["relationship_label_key"] in row
            else "",
        }

    # END _parse_relationship_edge

    @staticmethod
    def _parse_relationship_definition(data, definition, script_name="model_extractor", data_only=False):
        deduplicated_data = data[
            (data[definition["source_id_key"]] == data[definition["source_id_key"]])
            & (data[definition["target_id_key"]] == data[definition["target_id_key"]])
        ]
        deduplicated_data = deduplicated_data.drop_duplicates(subset=definition["id_key"])
        return {
            "metadata": (
                ExtractorLanguagePrimitives._parse_relationship_data(row, definition, script_name)
                for index, row in deduplicated_data.iterrows()
            ),
            "edges": (
                ExtractorLanguagePrimitives._parse_relationship_edge(row, definition)
                for index, row in deduplicated_data.iterrows()
                if not data_only
            ),
        }

    # END _parse_relationship_definition

    @staticmethod
    def parse_relationship(data, model, definitions, script_name="model extractor", data_only=False):
        """
        Use the provided definitions to generate edges from the given dataset.
        The edges returned are validated against the given model.

        :returns: A dictionary containing the edges and metadata generated.
        :rtype: {
            'edges': iterable,
            'metadata': iterable
        }

        :param pandas.DataFrame data: The dataset from which to generate
            the edges.
        :param Graph model: The model against which the edges should be
            validated.
        :param RelationshipDefinition | list of RelationshipDefinition
            definitions: The definitions that declare the edges to generate.
            You can also pass a single definition.
        :param str script_name: *Optional*. The name of the calling script for
            provenance. Defaults to 'model extractor'.
        :param boolean data_only: *Optional*. Whether or not the elements
            should be generated in addition to the data associated with them.
            Defaults to False.
        """

        # You can also pass a single definition into this function
        _definitions = iter(list(definitions))
        node_ids = list(model.nodes.id) if len(model.nodes) > 0 else []
        edges = iter([])
        metadata = iter([])
        for definition in _definitions:
            parsed_definition = ExtractorLanguagePrimitives._parse_relationship_definition(
                data, definition, script_name, data_only
            )
            edges = chain(
                edges,
                (
                    edge
                    for edge in parsed_definition["edges"]
                    if edge["source"] in node_ids and edge["target"] in node_ids
                ),
            )
            metadata = chain(metadata, parsed_definition["metadata"])
        # END LOOP

        return {"edges": edges, "metadata": metadata}

    # END parse_relationship

    @staticmethod
    def parse_view(data, model, ids, script_name="model extractor", data_only=False):
        """
        Use the provided definitions to generate views from the given dataset.
        The dataset is grouped into multiple views based on the id_key.

        :param pandas.DataFrame data: The dataset from which to generate
            the views.
        :param Graph model: The model that will contain the views.
        :param list of ViewDefinition ids: The definitions that declare the
            views to generate.
        :param str script_name: *Optional*. The name of the calling script for
            provenance. Defaults to 'model extractor'.
        :param boolean data_only: *Optional*. Whether or not the views should
            be generated in addition to the data associated with them.
            Defaults to False.
        """
        # create data
        edge_ids = []
        if len(model.edges) > 0:
            edge_ids = list(model.edges.id)
        views = []
        view_metadata = []

        for id_ in ids:
            # print(id_)
            if id_["id_type"] == "static":
                groups = [{"name": id_["id_value"], "data": data}]
            else:
                groups = []
                group_selectors = list(data[id_["id_key"]].unique())
                # print(group_selectors)
                for sel in group_selectors:
                    groups.append(
                        {
                            "name": "{}{}".format(id_["id_prefix"], sel),
                            "data": data[data[id_["id_key"]] == sel],
                        }
                    )
            for gr in groups:
                # create data
                # create view
                if not data_only:
                    gr_data = gr["data"]
                    if len(gr_data) > 0:
                        view = {"type": "ar3_Diagram"}
                        content = {"created_by": script_name, "m4i_id_type": id_["id_type"]}
                        if id_["id_type"] == "static":
                            view["id"] = id_["id_value"]
                            content["m4i_id_prefix"] = ""
                            content["m4i_original_id"] = str(id_["id_value"])
                        else:
                            view["id"] = "{}{}".format(id_["id_prefix"], gr_data.iloc[0][id_["id_key"]])
                            content["m4i_original_id"] = str(gr_data.iloc[0][id_["id_key"]])
                            content["m4i_id_prefix"] = id_["id_prefix"]
                        metadata = {"id": view["id"], "data": content}
                        view_metadata.append(metadata)
                        if id_["view_name_type"] == "static":
                            view["name"] = id_["view_name_value"]
                        else:
                            view["name"] = "{}{}".format(
                                id_["view_name_prefix"], gr_data.iloc[0][id_["view_name_key"]]
                            )
                        view_nodes = []
                        view_coordinates = {}
                        if "view_nodes" in id_:
                            for nn_ in id_["view_nodes"]:
                                if nn_["id_key"] in gr_data.columns:
                                    deduplicated_data = gr_data.drop_duplicates(subset=nn_["id_key"])
                                    for _index, row in deduplicated_data.iterrows():
                                        if row[nn_["id_key"]] == row[nn_["id_key"]]:
                                            nnn_ = "{}{}".format(nn_["id_prefix"], row[nn_["id_key"]])
                                            if nnn_ not in view_nodes:
                                                view_nodes.append(nnn_)
                                                # handle coordinates
                                                if "x" in nn_ and "y" in nn_:
                                                    nn_dict = {
                                                        "{}{}".format(nn_["id_prefix"], row[nn_["id_key"]]): [
                                                            nn_["x"],
                                                            nn_["y"],
                                                        ]
                                                    }
                                                    view_coordinates.update(nn_dict)
                                                elif (
                                                    "x_key" in nn_
                                                    and "y_key" in nn_
                                                    and nn_["x_key"] in row
                                                    and nn_["y_key"] in row
                                                    and isinstance(row[nn_["x_key"]], numbers.Number)
                                                    and isinstance(row[nn_["y_key"]], numbers.Number)
                                                    and not math.isnan(row[nn_["x_key"]])
                                                    and not math.isnan(row[nn_["y_key"]])
                                                ):
                                                    nn_dict = {
                                                        "{}{}".format(nn_["id_prefix"], row[nn_["id_key"]]): [
                                                            row[nn_["x_key"]],
                                                            row[nn_["y_key"]],
                                                        ]
                                                    }
                                                    view_coordinates.update(nn_dict)
                        if view_nodes == []:
                            view_nodes = None
                        view_edges = []
                        if "view_edges" in id_:
                            for ee_ in id_["view_edges"]:
                                if ee_["id_key"] in gr_data.columns:
                                    ee_list = [
                                        "{}{}".format(ee_["id_prefix"], dd)
                                        for dd in list(gr_data[ee_["id_key"]].unique())
                                        if dd in edge_ids
                                        and "{}{}".format(ee_["id_prefix"], dd) not in view_edges
                                    ]
                                    view_edges.extend(ee_list)
                        if view_edges == []:
                            view_edges = None
                        view_labels = []
                        label_ids = []
                        if "view_labels" in id_:
                            for nn_ in id_["view_labels"]:
                                if (
                                    nn_["id_key"] in gr_data.columns
                                    and nn_["x_key"] in gr_data.columns
                                    and nn_["y_key"] in gr_data.columns
                                    and nn_["width_key"] in gr_data.columns
                                    and nn_["height_key"] in gr_data.columns
                                    and nn_["name_key"] in gr_data.columns
                                ):
                                    rr_ = gr_data[
                                        [
                                            nn_["id_key"],
                                            nn_["x_key"],
                                            nn_["y_key"],
                                            nn_["width_key"],
                                            nn_["height_key"],
                                            nn_["name_key"],
                                        ]
                                    ]
                                    deduplicated_data = rr_.drop_duplicates(subset=nn_["id_key"])
                                    for _index, row in deduplicated_data.iterrows():
                                        label_id = "{}{}".format(nn_["id_prefix"], row[nn_["id_key"]])
                                        label_ = {
                                            "id": label_id,
                                            "x": 0,
                                            "y": 0,
                                            "width": 100,
                                            "height": 30,
                                            "name": "",
                                        }
                                        if nn_["x_key"] in row and row[nn_["x_key"]] == row[nn_["x_key"]]:
                                            label_["x"] = int(round(float(row[nn_["x_key"]])))
                                        if nn_["y_key"] in row and row[nn_["y_key"]] == row[nn_["y_key"]]:
                                            label_["y"] = int(round(float(row[nn_["y_key"]])))
                                        if (
                                            nn_["width_key"] in row
                                            and row[nn_["width_key"]] == row[nn_["width_key"]]
                                        ):
                                            label_["width"] = int(round(float(row[nn_["width_key"]])))
                                        if (
                                            nn_["height_key"] in row
                                            and row[nn_["height_key"]] == row[nn_["height_key"]]
                                        ):
                                            label_["height"] = int(round(float(row[nn_["height_key"]])))
                                        if (
                                            nn_["name_key"] in row
                                            and row[nn_["name_key"]] == row[nn_["name_key"]]
                                        ):
                                            label_["name"] = row[nn_["name_key"]]
                                        if label_id not in label_ids:
                                            label_ids.append(label_id)
                                            view_labels.append(label_)
                        view_path = ["Views"]
                        if "view_path" in id_:
                            for vv_ in id_["view_path"]:
                                if vv_["type"] == "static":
                                    view_path.append(vv_["value"])
                                else:
                                    if vv_["value"] in gr_data.columns:
                                        if isinstance(gr_data.iloc[0][vv_["value"]], list):
                                            view_path.extend(
                                                [
                                                    "{}{}".format(vv_["prefix"], x)
                                                    for x in gr_data.iloc[0][vv_["value"]]
                                                ]
                                            )
                                        else:
                                            view_path.append(
                                                "{}{}".format(vv_["prefix"], gr_data.iloc[0][vv_["value"]])
                                            )
                            content["m4i_path"] = "/".join(view_path)
                        views.append(
                            ArchimateUtils.generate_view(
                                model,
                                name=view["name"],
                                view_id=view["id"],
                                nodes=view_nodes,
                                edges=view_edges,
                                layout=id_["view_layout"],
                                path=view_path,
                                coords=view_coordinates,
                                labels=view_labels,
                            )
                        )

        return {"views": views, "metadata": view_metadata}

    # END parse_view


# END ExtractorLanguagePrimitives
