import contextlib
import copy
import json
import uuid
import warnings
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from enum import Enum
from itertools import chain
from typing import Optional, Union

import numpy as np
from pandas import DataFrame

from m4i_analytics.graphs.GraphUtils import GraphUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Archi import ArchiElement
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType,
    RelationshipType,
)
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import (
    ArchimateModel,
    ViewAttribute,
)
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute
from m4i_analytics.graphs.visualisations.GraphPlotter import Layout as LayoutEnum
from m4i_analytics.graphs.visualisations.model.Layout import Layout
from m4i_analytics.m4i.M4IUtils import M4IUtils
from m4i_analytics.m4i.platform.PlatformApi import PlatformApi
from m4i_analytics.m4i.platform.PlatformUtils import PlatformUtils


class ModelFormat(Enum):
    """
    Each entry corresponds to a format in which a model can be encoded.
    XML corresponds to the Open Group XML Exchange format.
    """

    ARCHI = "archimate"
    JSON = "json"
    XML = "xml"


# END ModelFormat


class ArchimateUtils(GraphUtils):
    PARSER_NAME = "archimate3"

    @staticmethod
    def retrieve_model(
        branchName,
        userid,
        projectOwner=None,
        projectName=None,
        fullProjectName=None,
        modelId="TRUNK",
        withViews=True,
        version=None,
        format=ModelFormat.JSON,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Retrieves a raw model string in the specified format from the repository,
        matching the parameters provided.

        :returns: A raw model string of the model matching the parameters.
        :rtype: str

        :param str branchName: The specific branch of the model you wish to retrieve.
        :param str userid: The name of the user performing this action.
        :param str projectOwner: *Optional*. Username of the owner of the
            project containing the model. Supply either this and the project name,
            or the full project name. Defaults to None.
        :param str projectName: *Optional*. Name of the project containing the
            model. Supply either this and the project owner, or the full project
            name. Defaults to None.
        :param str fullProjectName: *Optional*. Fully qualified name of the
            project as retrieved from the repository. Supply either this, or the
            project owner and project name. Defaults to None.
        :param boolean withViews: *Optional*. Whether the retrieved model should
            contain views. For analysis, views are often not used and can be
            omitted when downloading the model.
        :param long version: *Optional*. The version of the model to retrieve.
            If empty, retrieves the latest version. Empty by default.
        :param ModelFormat format: *Optional*. Format to retrieve the model.
            Defaults to ModelFormat.JSON.

        :exception TypeError: Thrown when any parameter (excluding version)
            is not defined.
        :exception ValueError: Thrown when any parameter is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        if isinstance(format, ModelFormat):
            format = format.value

        if fullProjectName is None:
            if projectOwner is None or projectName is None:
                raise ValueError(
                    "Either fullProjectName or both projectOwner and projectName must be provided"
                )
            fullProjectName = M4IUtils.construct_model_id(projectOwner, projectName)

        result = PlatformApi.retrieve_model(
            branchName,
            fullProjectName,
            userid,
            contentType=format,
            withViews=withViews,
            version=version,
            parserName=ArchimateUtils.PARSER_NAME,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        return result

    # END retrieve_model

    @staticmethod
    def _load_name(model, format: Union[ModelFormat, str] = ModelFormat.JSON):
        name = None

        if isinstance(format, ModelFormat):
            format = format.value

        if format == ModelFormat.JSON.value:
            root = model["ar3_model"]
            name = "Archimate model"
            with contextlib.suppress(Exception):
                name = root["ar3_name"][0]["value"]

        elif format == ModelFormat.ARCHI.value or format == ModelFormat.XML.value:
            pass

        return name

    # END _load_name

    @staticmethod
    def _load_elements(model, format: Union[ModelFormat, str] = ModelFormat.JSON):
        nodes = None

        if isinstance(format, ModelFormat):
            format = format.value

        if format == ModelFormat.JSON.value:

            def load_type(n):
                # First, try to get the type from the ArchiMate metamodel
                result = ElementType.getElementByTag(n["@xsi_type"])

                # If no match was found, check whether we're dealing with an Archi-specific element
                if result is None:
                    result = ArchiElement.getElementByTag(n["@xsi_type"])

                # If still no match is found, issue a warning to the user
                if result is None:
                    warnings.warn(
                        "Type {} of node {} is not recognized. The node will"
                        " not be included in the loaded model.".format(n["@xsi_type"], n["@identifier"]),
                        stacklevel=2,
                    )

                return result

            # END load_type

            root = model["ar3_model"]
            elems = root["ar3_elements"]["ar3_element"]

            nodes = list(
                map(
                    lambda n: {
                        "id": n["@identifier"],
                        "name": n["ar3_name"][0]["value"] if "ar3_name" in n else "",
                        "label": n["ar3_name"][0]["value"] if "ar3_name" in n else "",
                        "type": load_type(n),
                    },
                    elems,
                )
            )

            nodes = [node for node in nodes if node["type"] is not None]

        elif format == ModelFormat.ARCHI.value or format == ModelFormat.XML.value:
            pass

        result = DataFrame(nodes)

        return result

    # END _load_elements

    @staticmethod
    def _load_relationships(model, format: Union[ModelFormat, str] = ModelFormat.JSON):
        def fmt_attributes(relationship):
            result = {}
            if relationship["@xsi_type"] == RelationshipType.ACCESS["tag"]:
                result["accessType"] = relationship.get(
                    "@accessType",
                    RelationshipType.ACCESS_ACCESS["attributes"]["accessType"],
                )
            elif (
                relationship["@xsi_type"] == RelationshipType.ASSOCIATION["tag"]
                and "@isDirected" in relationship
            ):
                result["isDirected"] = relationship["@isDirected"]
            # END IF
            return result

        # END fmt_attributes

        edges = None

        if isinstance(format, ModelFormat):
            format = format.value

        if format == ModelFormat.JSON.value:

            def load_type(r):
                result = RelationshipType.getRelationshipByTag(r["@xsi_type"], fmt_attributes(r))
                if not result:
                    warnings.warn(
                        "Type {} of relationship {} is not recognized. The"
                        " relationship will not be included in the loaded model.".format(
                            r["@xsi_type"], r["@identifier"]
                        ),
                        stacklevel=2,
                    )
                return result

            # END load_type

            root = model["ar3_model"]
            rels = root["ar3_relationships"]["ar3_relationship"]

            edges = list(
                map(
                    lambda r: {
                        "id": r["@identifier"],
                        "name": r["ar3_name"][0]["value"] if "ar3_name" in r else "",
                        "label": r["ar3_name"][0]["value"] if "ar3_name" in r else "",
                        "source": r["@source"],
                        "target": r["@target"],
                        "type": load_type(r),
                        "is_bidirectional": False,
                    },
                    rels,
                )
            )

            edges = [edge for edge in edges if edge["type"] is not None]

        elif format == ModelFormat.ARCHI.value or format == ModelFormat.XML.value:
            pass

        result = DataFrame(edges)

        return result

    # END _load_relationships

    @staticmethod
    def _load_views(model, format: Union[ModelFormat, str] = ModelFormat.JSON):
        viewset = None

        if isinstance(format, ModelFormat):
            format = format.value

        if format == ModelFormat.JSON.value:
            root = model["ar3_model"]
            views = root["ar3_views"]["ar3_diagrams"]["ar3_view"]

            def view_mapper(view):
                result = {
                    "id": view["@identifier"],
                    "name": view["ar3_name"][0]["value"] if "ar3_name" in view else "",
                    "type": view["@xsi_type"],
                    "connections": None,
                    "nodes": None,
                    "properties": None,
                }

                if "ar3_connection" in view:
                    result["connections"] = view["ar3_connection"]

                if "ar3_node" in view:
                    result["nodes"] = view["ar3_node"]

                if "ar3_properties" in view and "ar3_property" in view["ar3_properties"]:
                    result["properties"] = view["ar3_properties"]["ar3_property"]

                return result

            # END view_mapper

            viewset = list(map(lambda view: view_mapper(view), views))

        elif format == ModelFormat.ARCHI.value or format == ModelFormat.XML.value:
            pass

        result = DataFrame(viewset)

        return result

    # END _load_views

    @staticmethod
    def _load_organizations(model, format: Union[ModelFormat, str] = ModelFormat.JSON):
        organizations = None

        if isinstance(format, ModelFormat):
            format = format.value

        if format == ModelFormat.JSON.value:
            root = model["ar3_model"]
            orgs = root["ar3_organizations"]

            def organization_mapper(organization, levels=None, depth=0):
                if levels is None:
                    levels = {}
                result = []
                levels = levels.copy()

                keys = organization.keys()

                if "ar3_label" in keys:
                    levels["level" + str(depth)] = organization["ar3_label"][0]["value"]

                if "ar3_item" in keys:
                    result += [
                        item
                        for list in map(
                            lambda o: organization_mapper(o, levels, depth + 1),
                            organization["ar3_item"],
                        )
                        for item in list
                    ]

                if "@identifierRef" in keys:
                    result.append(dict(idRef=organization["@identifierRef"], **levels))

                return result

            # END organization_mapper

            organizations = [item for list in map(lambda o: organization_mapper(o), orgs) for item in list]

        elif format == ModelFormat.ARCHI.value or format == ModelFormat.XML.value:
            pass

        result = DataFrame(organizations)

        # This adds a none column to the end of the dataframe to ensure
        # organizations can be exported consistently as JSON.
        result["level" + str(len(list(result.columns)))] = None
        # Sometimes nan values appear instead of None values, but further
        # processing expects None. Nan values produce extra folders and cause
        # problems with RestApi.
        result = result.applymap(lambda x: x if x == x else None)

        return result

    # END _load_organizations

    @staticmethod
    def load_model(raw_model, raw_data=None, withViews=True, format=ModelFormat.JSON):
        """
        Loads the provided raw model (as retrieved from the repository) into an
        ArchimateModel instance, which provides separate Pandas Dataframes of
        the nodes, edges, views and organizations in your model.

        :returns: An ArchimateModel instance containing the nodes, edges, views
            and organizations as separate Pandas Dataframes.
        :rtype: ArchimateModel

        :param str raw_model: The unparsed model string from the repository.
        :param DataRetrieve raw_data: The unparsed data from the repository.
        :param ModelFormat format: The format in which you retrieved the model.
            This needs to match the actual format for loading to succeed.

        :exception ValueError: Thrown when the raw model could not be parsed
            as the expected format.
        """

        model = None

        if isinstance(format, ModelFormat):
            format = format.value

        if format == ModelFormat.JSON.value:
            model = json.loads(raw_model)

        elif format == ModelFormat.ARCHI.value or format == ModelFormat.XML.value:
            model = ET.fromstring(raw_model)

        result = ArchimateModel(
            **{
                "name": ArchimateUtils._load_name(model, format),
                "nodes": ArchimateUtils._load_elements(model, format),
                "edges": ArchimateUtils._load_relationships(model, format),
                "views": ArchimateUtils._load_views(model, format)
                if withViews
                else DataFrame(columns=["id", "name", "type", "nodes", "connections", "properties"]),
                "organizations": ArchimateUtils._load_organizations(model, format),
                "defaultAttributeMapping": True,
            }
        )

        if raw_data:
            GraphUtils.loadGraphData(result, raw_data)

        return result

    # END load_model

    @staticmethod
    def load_model_from_repository(
        branchName,
        userid,
        projectOwner=None,
        projectName=None,
        fullProjectName=None,
        modelId="TRUNK",
        version=None,
        format=ModelFormat.JSON,
        withData=False,
        withViews=True,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Retrieves a model matching the parameters from the repository and loads
        it into an ArchimateModel instance.

        :returns: An ArchimateModel instance containing nodes and relationships
            as separate Pandas Dataframes.
        :rtype: ArchimateModel

        :param str branchName: The specific branch of the model to retrieve.
        :param str userid: The name of the user performing this action.
        :param str projectOwner: *Optional*. Username of the owner of the
            project. Supply either this and the project name, or full project
            name. Defaults to None.
        :param str projectName: *Optional*. Name of the project containing the
            model. Supply either this and the project owner, or full project
            name. Defaults to None.
        :param str fullProjectName: *Optional*. Fully qualified name of the
            project as retrieved from the repository. Supply either this, or
            project owner and project name. Defaults to None.
        :param long version: *Optional*. Version of the model to retrieve.
            If empty, retrieves latest version. Empty by default.
        :param ModelFormat format: *Optional*. Format to retrieve the model.
            Defaults to ModelFormat.JSON.

        :exception TypeError: Thrown when any parameter (excluding version)
            is not defined.
        :exception ValueError: Thrown when any parameter is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        model = ArchimateUtils.retrieve_model(
            branchName,
            userid,
            projectOwner,
            projectName,
            fullProjectName,
            modelId,
            withViews,
            version,
            format,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        data = (
            PlatformUtils.retrieve_data(
                projectOwner=projectOwner,
                projectName=projectName,
                fullProjectName=fullProjectName,
                modelId=modelId,
                branchName=branchName,
                parserName="archimate3",
                username=username,
                password=password,
                totp=totp,
                access_token=access_token,
            )
            if withData
            else None
        )

        return ArchimateUtils.load_model(model, raw_data=data, format=format, withViews=withViews)

    # END load_model

    @staticmethod
    def to_JSON(model):
        """
        Converts an archimate model to a JSON string that can be ingested by the M4I repository.

        :returns: A JSON string representing the given model.
        :rtype: str

        :param ArchimateModel model: The model you want to convert to a JSON string.
        """

        def format_element(id_, type_, name):
            return {
                "@identifier": id_,
                "@xsi_type": type_["tag"],
                "ar3_name": [{"@xml_lang": "en", "value": str(name)}],
            }

        # END format_element

        def format_relationship(id_, type_, name, source, target):
            result = {
                "@identifier": id_,
                "@target": target,
                "@source": source,
                "@xsi_type": type_["tag"],
                "ar3_name": [{"@xml_lang": "en", "value": str(name)}],
            }
            if type_.is_instance_of(RelationshipType.ACCESS):
                result["@accessType"] = type_["attributes"]["accessType"]
            if type_.is_instance_of(RelationshipType.ASSOCIATION):
                result["@isDirected"] = type_["attributes"]["isDirected"]
            return result

        # END format_relationship

        def format_view(id_, type_, nodes, connections, name):
            return {
                "@identifier": id_,
                "@xsi_type": type_,
                "ar3_node": nodes if nodes is not None else [],
                "ar3_connection": connections if connections is not None else [],
                "ar3_name": [{"@xml_lang": "en", "value": str(name)}],
            }

        # END format_view

        def format_organizations(orgs):
            levels = [colname for colname in orgs if colname.startswith("level")]
            levels.sort()

            root = {"ar3_item": []}

            def find_item(root, name):
                return next(
                    (
                        item
                        for item in root["ar3_item"]
                        if next(iter(item.get("ar3_label", [])), {}).get("value") == name
                    ),
                    None,
                )

            # END find_item

            def format_label(name):
                return {
                    "ar3_label": [{"@xml_lang": "en", "value": str(name)}],
                    "ar3_item": [],
                }

            # END format_label

            def format_item(id):
                return {"@identifierRef": id}

            # END format_item

            def parse_organization(org, current_root=root, depth=0):
                name = org[levels[depth]]

                if name and depth < (len(levels) - 1):
                    item = find_item(current_root, name)

                    if not item:
                        item = format_label(name)
                        current_root["ar3_item"].append(item)

                    parse_organization(org, item, depth + 1)
                else:
                    current_root["ar3_item"].append(format_item(org["idRef"]))

            # END parse_organization

            for org in orgs.to_dict(orient="records"):
                parse_organization(org)
            # END LOOP

            return [root]

        # END format_organization

        elems = [
            format_element(
                row[model.getNodeAttributeMapping(NodeAttribute.ID)],
                row[model.getNodeAttributeMapping(NodeAttribute.TYPE)],
                row[model.getNodeAttributeMapping(NodeAttribute.NAME)],
            )
            for row in model.nodes.to_dict(orient="records")
        ]

        relations = [
            format_relationship(
                row[model.getEdgeAttributeMapping(EdgeAttribute.ID)],
                row[model.getEdgeAttributeMapping(EdgeAttribute.TYPE)],
                row[model.getEdgeAttributeMapping(EdgeAttribute.NAME)],
                row[model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)],
                row[model.getEdgeAttributeMapping(EdgeAttribute.TARGET)],
            )
            for row in model.edges.to_dict(orient="records")
        ]

        views = [
            format_view(
                row[model.getViewAttributeMapping(ViewAttribute.ID)],
                row[model.getViewAttributeMapping(ViewAttribute.TYPE)],
                row[model.getViewAttributeMapping(ViewAttribute.NODES)],
                row[model.getViewAttributeMapping(ViewAttribute.CONNECTIONS)],
                row[model.getViewAttributeMapping(ViewAttribute.NAME)],
            )
            for row in model.views.to_dict(orient="records")
        ]

        organizations = format_organizations(model.organizations)

        model_dict = {
            "ar3_model": {
                "@identifier": str(model.name),
                "ar3_name": [{"@xml_lang": "en", "value": str(model.name)}],
                "ar3_elements": {"ar3_element": elems},
                "ar3_relationships": {"ar3_relationship": relations},
                "ar3_views": {"ar3_diagrams": {"ar3_view": views}},
                "ar3_organizations": organizations,
            }
        }

        return json.dumps(model_dict)

    # END to_JSON

    @staticmethod
    def generate_view(
        model: ArchimateModel,
        view_id: Optional[str] = None,
        nodes: Optional[list[str]] = None,
        edges: Optional[list[str]] = None,
        viewpoint: Optional[str] = None,
        layout: Optional[Union[Layout, LayoutEnum]] = None,
        name: str = "Generated view",
        coords: Optional[dict] = None,
        labels: Optional[list] = None,
        node_width: int = 120,
        node_height: int = 55,
        path: Optional[list[str]] = None,
    ):
        """
        Generate a view containing the given nodes.

        :returns: The generated view keyed by the attribute mappings of the model.

        :param ArchimateModel model: The model for which you want to generate a view.
        :param list nodes: *Optional*. List of node ids to include in the view.
            If None (default), includes all nodes.
        :param list edges: *Optional*. List of edge ids to include in the view.
            If None, includes all edges between selected nodes. Default is None.
        :param any viewpoint: *Optional*. Viewpoint to apply to the view.
            Only nodes fitting the viewpoint are included. Default is None.
        :param Layout layout: *Optional*. Layout to apply to nodes (affects
            node coordinates). Default is Layout.RANDOM.
        :param str name: *Optional*. The name of the view.
        :param dict coords: *Optional*. Dictionary of positions per node for manual layout.
        """

        if path is None:
            path = ["Generated views"]
        if labels is None:
            labels = []
        if coords is None:
            coords = {}
        if not view_id:
            view_id = str(uuid.uuid4())

        def find_viewnodes(viewnodes, nodeid):
            return [viewnode["@identifier"] for viewnode in viewnodes if viewnode["@elementRef"] == nodeid]

        # END find_viewnodes

        def format_view(viewid, nodes, edges):
            return {
                model.getViewAttributeMapping(ViewAttribute.ID): viewid,
                model.getViewAttributeMapping(ViewAttribute.TYPE): "ar3_Diagram",
                model.getViewAttributeMapping(ViewAttribute.NAME): name,
                model.getViewAttributeMapping(ViewAttribute.NODES): nodes,
                model.getViewAttributeMapping(ViewAttribute.CONNECTIONS): edges,
                model.getViewAttributeMapping(ViewAttribute.PROPERTIES): [],
            }

        # END format_view

        def format_label(label):
            return {
                "@identifier": label["id"],
                "@x": label["x"],
                "@y": label["y"],
                "@w": label["width"],
                "@h": label["height"],
                "@xsi_type": "ar3_Label",
                "@textAlignment": 1,
                "ar3_label": [{"@xml_lang": "en", "value": label["name"]}],
            }

        # END format_label

        def format_node(view_id, nodeid, x, y, w, h, ii=1):
            return {
                "@identifier": f"{view_id}-{nodeid}--{ii}",
                "@x": x,
                "@y": y,
                "@w": w,
                "@h": h,
                "@elementRef": nodeid,
                "@xsi_type": "ar3_Element",
            }

        # END format_node

        def format_edge(view_id, edgeid, sourceid, targetid, ii=1):
            return {
                "@identifier": f"{view_id}-{edgeid}--{ii}",
                "@source": sourceid,
                "@target": targetid,
                "@relationshipRef": edgeid,
                "@xsi_type": "ar3_Relationship",
            }

        # END format_edge

        viewmodel = copy.deepcopy(model)

        if nodes:
            viewmodel.nodes = viewmodel.nodes[
                viewmodel.nodes[viewmodel.getNodeAttributeMapping(NodeAttribute.ID)].isin(nodes)
            ]

            viewmodel.edges = viewmodel.edges[
                np.logical_and(
                    viewmodel.edges[viewmodel.getEdgeAttributeMapping(EdgeAttribute.SOURCE)].isin(
                        viewmodel.nodes[viewmodel.getNodeAttributeMapping(NodeAttribute.ID)]
                    ),
                    viewmodel.edges[viewmodel.getEdgeAttributeMapping(EdgeAttribute.TARGET)].isin(
                        viewmodel.nodes[viewmodel.getNodeAttributeMapping(NodeAttribute.ID)]
                    ),
                )
            ]
        if edges:
            viewmodel.edges = viewmodel.edges[
                viewmodel.edges[viewmodel.getEdgeAttributeMapping(EdgeAttribute.ID)].isin(edges)
            ]

        if layout is None:
            from m4i_analytics.graphs.visualisations.ManualLayout import ManualLayout

            layout = ManualLayout()
        assert layout is not None

        # Handle both Layout ABC instances and LayoutEnum values
        if isinstance(layout, Enum):
            from m4i_analytics.graphs.visualisations.GraphPlotter import GraphPlotter

            coords = GraphPlotter.get_coordinates(
                viewmodel,
                layout=layout,
                node_width=node_width,
                node_height=node_height,
            )
        else:
            coords = layout.get_coordinates(
                viewmodel, coords=coords, node_width=node_width, node_height=node_height
            )
        assert coords is not None, "Layout coordinates could not be generated"

        viewlabels = [format_label(label) for label in labels or []]
        viewnodes = []
        ii = 0
        for key in coords:
            node_ref = next(
                iter(
                    model.nodes[model.nodes[model.getNodeAttributeMapping(NodeAttribute.ID)] == key].to_dict(
                        orient="records"
                    )
                ),
                {},
            )
            node_type = node_ref.get(model.getNodeAttributeMapping(NodeAttribute.TYPE))
            # Make an exception for junctions..
            is_junction = (
                node_type
                in [
                    ElementType.JUNCTION,
                    ElementType.AND_JUNCTION,
                    ElementType.OR_JUNCTION,
                ]
                if node_type
                else False
            )
            viewnodes.append(
                format_node(
                    view_id,
                    key,
                    int(round(float(coords[key][0]))),
                    int(round(float(coords[key][1]))),
                    node_width if not is_junction else 14,
                    node_height if not is_junction else 14,
                    ii,
                )
            )
            ii = ii + 1
        # END LOOP

        viewedges = []
        ii = 0
        for viewedge in viewmodel.edges.to_dict(orient="records"):
            edgeid = viewedge[viewmodel.getEdgeAttributeMapping(EdgeAttribute.ID)]
            sources = find_viewnodes(
                viewnodes,
                viewedge[viewmodel.getEdgeAttributeMapping(EdgeAttribute.SOURCE)],
            )
            targets = find_viewnodes(
                viewnodes,
                viewedge[viewmodel.getEdgeAttributeMapping(EdgeAttribute.TARGET)],
            )

            for source in sources:
                for target in targets:
                    viewedges.append(format_edge(view_id, edgeid, source, target, ii))
                    ii = ii + 1
                # END LOOP
            # END LOOP
        # END LOOP

        view = format_view(view_id, viewlabels + viewnodes, viewedges)
        model.views = model.views.append(view, ignore_index=True)

        organization_path = {"idRef": view_id}

        for index, level in enumerate(path):
            organization_path[f"level{str(index + 1)}"] = level
        # END LOOP

        organization_path[f"level{str(len(path) + 1)}"] = ""

        model.organizations = model.organizations.append(organization_path, ignore_index=True)
        model.organizations.fillna("")

        return view

    # END generate_view

    @staticmethod
    def sliceByEdgeType(model, edge_types):
        """
        Slice a model by the specified edge types. The resulting model will
        contain only these edge types, as well as any connected nodes.

        :returns: A model sliced by the specified edge types.
        :rtype: ArchimateModel

        :param list edge_types: A list of the edge types to slice by.
        """

        relationships = model.edges
        rels = relationships[relationships.type.isin(edge_types)]

        elem_ids = list(rels.source.unique()) + list(rels.target.unique())
        elements = model.nodes
        elems = elements[elements.id.isin(elem_ids)]

        organizations = model.organizations
        orgs = organizations[organizations.idRef.isin(elem_ids)]

        return ArchimateModel(
            **{
                "name": model.name + " slice for " + str(edge_types),
                "nodes": elems,
                "edges": rels,
                "views": DataFrame(columns=["id", "name", "type", "connections", "nodes", "properties"]),
                "organizations": orgs,
                "defaultAttributeMapping": True,
            }
        )

    # END sliceByEdgeType

    @staticmethod
    def slicebyNodeType(model, node_types):
        """
        Slice a model by the specified node types. The resulting model will
        contain only these node types, as well as any edges connecting them.

        :returns: A model sliced by the specified node types.
        :rtype: ArchimateModel

        :param list edge_types: A list of the node types to slice by.
        """

        nodes = model.nodes
        sliced_nodes = nodes[nodes.type.isin(node_types)]

        relations = model.edges
        sliced_relations = relations[
            relations.source.isin(sliced_nodes.id) or relations.target.isin(sliced_nodes.id)
        ]

        organizations = model.organizations
        sliced_organizations = organizations[organizations.idRef.isin(sliced_nodes.id)]

        return ArchimateModel(
            **{
                "name": model.name + " slice for " + str(node_types),
                "nodes": sliced_nodes,
                "edges": sliced_relations,
                "views": DataFrame(columns=["id", "name", "type", "connections", "nodes", "properties"]),
                "organizations": sliced_organizations,
                "defaultAttributeMapping": True,
            }
        )

    # END sliceByNodeType

    @staticmethod
    def commit_model_to_repository(
        model,
        projectName,
        projectOwner,
        branchName,
        userid,
        description,
        modelId="TRUNK",
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Commit a model to the Models4Insight model repository.

        :returns: A ModelCommit instance describing the commit operation.
            Note that the commit happens asynchronously on the server side.
            Monitor progress via query_model requests.
        :rtype: ModelCommit

        :param File model: The model you wish to commit.
        :param str projectName: The name of the project for the commit.
        :param str projectOwner: The username of the user who owns the project.
        :param str branchName: The name of the branch for the commit.
        :param str userid: The id of the user committing the model.
        :param str description: Describe the purpose of your commit.

        :exception TypeError: Thrown when any parameter (excluding module) is
            undefined or the result cannot be parsed into a ModelCommit instance.
        :exception ValueError: Thrown when any parameter is invalid or the
            result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        result = PlatformUtils.commit_model_to_repository(
            ArchimateUtils.to_JSON(model),
            projectName,
            projectOwner,
            branchName,
            userid,
            ModelFormat.JSON.value,
            ArchimateUtils.PARSER_NAME,
            modelId,
            description,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        return result

    # END commit_model_to_repository

    @staticmethod
    def commit_model_to_repository_with_conflict_resolution(
        model,
        projectName,
        projectOwner,
        branchName,
        userid,
        description,
        conflict_resolution_template,
        modelId="TRUNK",
        model_query_interval=1,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Commit a model to the Models4Insight model repository with conflict
        resolution.

        :returns: A ModelCommit instance describing the commit operation.
            Note that the commit happens asynchronously on the server side.
            Monitor progress via query_model requests.
        :rtype: ModelCommit

        :param File model: The model you wish to commit.
        :param str projectName: The name of the project for the commit.
        :param str projectOwner: The username of the user who owns the project.
        :param str branchName: The name of the branch for the commit.
        :param str userid: The id of the user committing the model.
        :param str description: Describe the purpose of your commit.

        :exception TypeError: Thrown when any parameter (excluding module) is
            undefined or the result cannot be parsed into a ModelCommit instance.
        :exception ValueError: Thrown when any parameter is invalid or the
            result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        result = PlatformUtils.commit_to_repository_resolve_conflict(
            model=ArchimateUtils.to_JSON(model),
            projectName=projectName,
            projectOwner=projectOwner,
            branch=branchName,
            userid=userid,
            parserName=ArchimateUtils.PARSER_NAME,
            model_query_interval=model_query_interval,
            description=description,
            conflict_resolution_template=conflict_resolution_template,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        return result

    # END commit_model_to_repository

    @staticmethod
    def color_view_node(
        view_node: dict,
        fill_color_red: int,
        fill_color_green: int,
        fill_color_blue: int,
    ):
        """
        Adds the given fill color to the given view node. The fill color is specified in RGB format.

        :returns: A copy of the view node with the given fill color set as a property.
        :rtype: dict

        :param dict view_node: The view node for which to set the fill color
        :param int fill_color_red: The redness of the fill color between 0-255
        :param int fill_color_green: The greenness of the fill color between 0-255
        :param int fill_color_blue: The blueness of the fill color  between 0-255
        """

        if fill_color_red < 0 or fill_color_red > 255:
            raise ValueError("Redness should be specified as a number between 0 and 255")
        # END IF

        if fill_color_green < 0 or fill_color_green > 255:
            raise ValueError("Greenness should be specified as a number between 0 and 255")
        # END IF

        if fill_color_blue < 0 or fill_color_blue > 255:
            raise ValueError("Blueness should be specified as a number between 0 and 255")
        # END IF

        return {
            **view_node,
            "ar3_style": {
                **view_node.get("ar3_style", {}),
                "ar3_fillColor": {
                    "@r": fill_color_red,
                    "@g": fill_color_green,
                    "@b": fill_color_blue,
                },
            },
        }

    # END color_view_node

    @staticmethod
    def color_view_edge(
        view_edge: dict,
        line_color_red: int,
        line_color_green: int,
        line_color_blue: int,
    ):
        """
        Adds the given line color to the given view edge. The line color is specified in RGB format.

        :returns: A copy of the view edge with the given line color set as a property.
        :rtype: dict

        :param dict view_edge: The view edge/connection for which to set the line color
        :param int line_color_red: The redness of the fill line between 0-255
        :param int line_color_green: The greenness of the line color between 0-255
        :param int line_color_blue: The blueness of the line color  between 0-255
        """

        if line_color_red < 0 or line_color_red > 255:
            raise ValueError("Redness should be specified as a number between 0 and 255")
        # END IF

        if line_color_green < 0 or line_color_green > 255:
            raise ValueError("Greenness should be specified as a number between 0 and 255")
        # END IF

        if line_color_blue < 0 or line_color_blue > 255:
            raise ValueError("Blueness should be specified as a number between 0 and 255")
        # END IF

        return {
            **view_edge,
            "ar3_style": {
                **view_edge.get("ar3_style", {}),
                "ar3_lineColor": {
                    "@r": line_color_red,
                    "@g": line_color_green,
                    "@b": line_color_blue,
                },
            },
        }

    # END color_view_edge

    @staticmethod
    def get_view_nodes(view_nodes: Iterable[dict]) -> Iterable[dict]:
        """
        Returns a flat sequence of all given nodes and their children.

        :returns: A flat sequence of all given nodes and their children
        :rtype: Generator of dict

        :param Iterable view_nodes: The top level set of nodes in the view
        """
        for node in view_nodes:
            yield node
            # If the ar3_node field is present, this node has child nodes
            if "ar3_node" in node:
                yield from ArchimateUtils.get_view_nodes(node["ar3_node"])
                # END LOOP
            # END IF
        # END LOOP

    # END get_view_nodes

    @staticmethod
    def get_view_nodes_child_parent_pairs(
        view_nodes: Iterable[dict], parent: Optional[str] = None
    ) -> Iterable[tuple[str, Optional[str]]]:
        """
        Returns a flat sequence of tuples representing the given nodes and their direct parents.
        The returned sequence also includes the children of the given nodes.

        :returns: A flat sequence of tuples representing the given nodes and their direct parents
        :rtype: Generator of (str, str)

        :param Iterable view_nodes: The top level set of nodes in the view
        :param str parent: *Optional*. The node id of the parent node for the given `view_nodes`
        """
        for node in view_nodes:
            # Continue only if the node is an element
            if "@elementRef" in node:
                node_id = node["@elementRef"]
                yield (node_id, parent)
                # If the ar3_node field is present, this node has child nodes
                if "ar3_node" in node:
                    yield from ArchimateUtils.get_view_nodes_child_parent_pairs(node["ar3_node"], node_id)
                    # END LOOP
                # END IF
            # END IF
        # END LOOP

    # END get_view_nodes_child_parent_pairs

    @staticmethod
    def get_view_object_by_id(view: dict, object_id: str) -> Optional[dict]:
        """
        Finds the view object (node, edge or other) with the given ID. Also checks nested objects.

        :return: The view object with the given id
        :rtype: dict

        :param view: The view to search in
        :type view: dict
        :param object_id: The id of the element to search for
        :type object_id: str
        """
        result = None
        if view is not None and "nodes" in view and "edges" in view:
            view_edges = view["edges"] if view["edges"] is not None else []
            view_nodes = view["nodes"] if view["nodes"] is not None else []
            for view_object in chain(view_nodes, view_edges):
                if view_object["@identifier"] == view_object:
                    result = view_object
                elif "ar3_node" in view_object:
                    result = ArchimateUtils.get_view_object_by_id(view_object["ar3_node"], object_id)
                # END IF
                if result:
                    break
                # END IF
            # END LOOP
        # END IF
        return result

    # END get_view_node_by_id

    @staticmethod
    def get_view_node_by_element_id(view_nodes: Iterable[dict], node_id: str) -> Iterable[dict]:
        """
        Finds the view nodes that reference the model node with the given ID.
        Also checks nested elements.

        :return: The view nodes referencing the model node with the given id.
        :rtype: Iterable[dict]

        :param view_nodes: The set of view nodes to search in.
        :type view_nodes: Iterable
        :param node_id: The id of the model node for which to search.
        :type node_id: str
        """
        if view_nodes is not None:
            for node in view_nodes:
                if node is not None and "@elementRef" in node and node["@elementRef"] == node_id:
                    yield node
                # END IF
                if node is not None and "ar3_node" in node:
                    yield from ArchimateUtils.get_view_node_by_element_id(node["ar3_node"], node_id)
                # END IF
            # END LOOP
        # END IF

    # END get_view_node_by_node_id

    @staticmethod
    def get_view_edge_by_relationship_id(view_edges: Iterable[dict], relationship_id: str) -> Iterable[dict]:
        """
        Finds the view edges that reference the model relationship with the given relationship ID.

        :return: The view edges that reference the model relationship with the given id
        :rtype: Iterable[dict]

        :param view_edges: The set of edges to search in
        :type view_nodes: Iterable
        :param node_id: The id of the model relationship for which to search
        :type node_id: str
        """
        if view_edges is not None:
            for edge in view_edges:
                if "@relationshipRef" in edge and edge["@relationshipRef"] == relationship_id:
                    yield edge
                # END IF
            # END LOOP
        # END IF

    # END get_view_edge_by_relationship_id


# END ArchimateUtils
