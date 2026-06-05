import copy
import time

import networkx as nx
from networkx import NetworkXNoPath
from pandas import DataFrame

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute
from m4i_analytics.m4i.platform.PlatformUtils import PlatformUtils
from m4i_analytics.m4i.portal.DBUtils import DBUtils, InsertBehavior


class Pathing:
    """
    This class handles the creation of the dataset required to show the sankey
    diagram representing the path between two nodes in the model.
    """

    # This obviously needs to be a parameter for the script
    SOURCE_ID_PREFIX = "oms_equ_"
    TARGET_ID_PREFIX = "superset_dashboard-"

    model_options = None
    pathing_target_table = None
    timeseries_target_table = None
    allowed_relationship_types = []

    def __init__(
        self,
        model_options,
        pathing_target_table,
        timeseries_target_table,
        allowed_relationship_types=None,
    ):
        """
        :param dict model_options: A dictionary specifying the project name,
            project owner, branch name and user to which the project containing
            the model belongs.
        :param str pathing_target_table: The name of the table to which the
            pathing data should be written.
        :param str timeseries_target_table: The name of the table to which the
            status info should be written.
        :param list of RelationshipType allowed_relationship_types: *Optional*.
            Narrow down the possible paths by specifying which relationship types
            are allowed to be traversed. Defaults to an empty array, meaning all
            relationship types are valid.
        """

        if allowed_relationship_types is None:
            allowed_relationship_types = []
        self.model_options = model_options
        self.pathing_target_table = pathing_target_table
        self.timeseries_target_table = timeseries_target_table
        self.allowed_relationship_types = allowed_relationship_types

    # END __init__

    def run(self, data_only=False):
        """
        Calculate all shortest paths between the sources and targets that match
        the given prefixes and ids. Also includes all shortest paths between nodes
        that have a critical state and the target nodes. Uploads the result to the
        portal database.

        :params boolean data_only: Whether or not only the timeseries table should
            be updated.
        """

        # Index node attributes so we don't have to search for them every time
        node_measured_status_index = {}
        node_status_index = {}
        node_name_index = {}
        node_data_index = {}

        def get_nodes(model):
            data = model.data.to_dict(orient="records")
            node_ids = model.nodes[model.getNodeAttributeMapping(NodeAttribute.ID)].tolist()

            sources = (
                item["id"]
                for item in data
                if (
                    self.SOURCE_ID_PREFIX in item["data"].get("m4i_id_prefix", "")
                    or item["data"].get("measured_data_in", 0) == 3
                    or item["data"].get("measured_processing", 0) == 3
                    or item["data"].get("measured_service", 0) == 3
                    or item["data"].get("measured_data_out", 0) == 3
                )
                and item["id"] in node_ids
            )
            targets = (
                item["id"]
                for item in data
                if self.TARGET_ID_PREFIX in item["data"].get("m4i_original_id", "") and item["id"] in node_ids
            )

            return sources, targets

        # END get_nodes

        def prepare_model(model):
            # Create a working copy of the model so we don't modify the original
            working_copy = copy.deepcopy(model)

            # Translate all junctions into actual nodes and edges
            junctions = working_copy.nodes[
                working_copy.nodes["type"].isin([ElementType.AND_JUNCTION, ElementType.OR_JUNCTION])
            ]

            transition_matrix = ArchimateUtils.toTransitionMatrix(working_copy)

            junction_bypasses = []
            for junction in junctions.to_dict(orient="records"):
                junction_sources = transition_matrix[transition_matrix["target"] == junction["id"]].to_dict(
                    orient="records"
                )
                junction_targets = transition_matrix[transition_matrix["source"] == junction["id"]].to_dict(
                    orient="records"
                )

                junction_bypasses = junction_bypasses + [
                    {
                        "id": "{}-{}-{}".format(junction["id"], source["source"], target["target"]),
                        "source": source["source"],
                        "target": target["target"],
                        "type": source["type"],  # Assume the type of the relation going into the junction
                        "name": "",
                        "label": "",
                        "weight": 3,
                    }
                    for source in junction_sources
                    for target in junction_targets
                ]
            # END LOOP

            if junction_bypasses:
                working_copy.edges = working_copy.edges.append(junction_bypasses)

            # Remove all junctions from the model
            working_copy.nodes = working_copy.nodes[
                ~working_copy.nodes["type"].isin([ElementType.AND_JUNCTION, ElementType.OR_JUNCTION])
            ]
            working_copy.edges = working_copy.edges[
                ~working_copy.edges["source"].isin(junctions["id"])
                & ~working_copy.edges["target"].isin(junctions["id"])
            ]

            # Filter out all relationship types that we are not allowed to traverse
            edge_type_key = working_copy.getEdgeAttributeMapping(EdgeAttribute.TYPE)

            if self.allowed_relationship_types:
                working_copy.edges = working_copy.edges[
                    working_copy.edges[edge_type_key].isin(self.allowed_relationship_types)
                ]

            # Apply a default weight to all edges we didn't assign one to already
            if "weight" in working_copy.edges:
                working_copy.edges["weight"] = working_copy.edges["weight"].fillna(1)
            else:
                working_copy.edges["weight"] = 1

            return working_copy

        # END prepare_model

        def node_measured_status(data, id_):
            status = node_measured_status_index.get(id_)

            if status is None:
                # Retrieve the data for this node from the model
                data = (
                    node_data_index[id_]
                    if id_ in node_data_index
                    else next(iter(data[data.id == id_].to_dict(orient="records")), {}).get("data", {})
                )

                # Aggregate the node status to a single value and return it
                status = max(
                    data.get("measured_service", 0),
                    data.get("measured_processing", 0),
                    data.get("measured_data_in", 0),
                    data.get("measured_data_out", 0),
                )

                node_measured_status_index[id_] = status
            # END IF
            return status

        # END node_measured_status

        def node_combined_status(data, id_):
            status = node_status_index.get(id_)

            if status is None:
                # Retrieve the data for this node from the model
                data = (
                    node_data_index[id_]
                    if id_ in node_data_index
                    else next(iter(data[data.id == id_].to_dict(orient="records")), {}).get("data", {})
                )

                # Aggregate the node status to a single value and return it
                status = max(
                    data.get("combined_service", 0),
                    data.get("combined_processing", 0),
                    data.get("combined_data_in", 0),
                    data.get("combined_data_out", 0),
                )

                node_status_index[id_] = status
            # END IF

            return status

        # END node_combined_status

        def get_paths(model, sources, targets):
            def get_routes(nxgraph, route_source, route_target):
                # Calculate the shortest path from source to target.
                # This generates a list of paths including all nodes that are passed.
                # Return the set of routes between the source and the target along
                # with the status of each node in these routes, or an empty list
                # if no routes are found.
                try:
                    for path in nx.all_shortest_paths(nxgraph, route_source, route_target, weight="weight"):
                        yield {
                            "origin": source_id,
                            "destination": target_id,
                            "path": (
                                {
                                    "id": id_,
                                    "status": node_combined_status(model.data, id_),
                                    "measured_status": node_measured_status(model.data, id_),
                                }
                                for id_ in path
                            ),
                        }
                except NetworkXNoPath:
                    yield {
                        "origin": source_id,
                        "destination": target_id,
                        "path": iter([]),
                    }

            # END get_routes

            # Transform the graph for use with the nx library
            nxgraph = ArchimateUtils.toNXGraph(model).to_undirected()

            all_targets = list(targets)

            for source_id in sources:
                for target_id in all_targets:
                    yield get_routes(nxgraph, source_id, target_id)
                # END LOOP
            # END LOOP

        # END get_paths

        def fmt_name(model, id_):
            # Appends a number corresponding to the name of a node to ensure it's uniqueness.
            # The value corresponds to the current number of occurrences of that name.
            def uniqueify(n, appendage=2):
                result = f"{n} {appendage}"
                if result in node_name_index.values():
                    result = uniqueify(n, appendage + 1)
                return result

            # END uniqueify

            name = node_name_index.get(id_)

            if name is None:
                node_id_key = model.getNodeAttributeMapping(NodeAttribute.ID)
                node_name_key = model.getNodeAttributeMapping(NodeAttribute.NAME)

                name = next(
                    iter(model.nodes[model.nodes[node_id_key] == id_].to_dict(orient="records")),
                    {},
                ).get(node_name_key, "")

                if name in node_name_index.values():
                    name = uniqueify(name)

                node_name_index[id_] = name
            # END IF

            return name

        # END node_name

        def fmt_status(value):
            mapping = {1: "OK", 2: "WARN", 3: "CRIT"}
            return mapping.get(value, "UNK")

        # END fmt_status

        def fmt_color(value):
            mapping = {1: "#00FF00", 2: "#FFFF00", 3: "#FF0000"}
            return mapping.get(value, "#D3D3D3")

        # END fmt_color

        def fmt_path(model, path):
            prev_node = next(path["path"], {})  # Placeholder value in case the path is empty
            for node in path["path"]:
                yield {
                    "path_origin": fmt_name(model, path["origin"]),
                    "path_origin_id": path["origin"],
                    "path_destination": fmt_name(model, path["destination"]),
                    "path_destination_id": path["destination"],
                    "source": fmt_name(model, prev_node["id"]),
                    "source_id": prev_node["id"],
                    "source_color": fmt_color(prev_node["measured_status"]),
                    "target": fmt_name(model, node["id"]),
                    "target_id": node["id"],
                    "target_color": fmt_color(node["measured_status"]),
                    "status": fmt_status(prev_node["status"]),
                    "color": fmt_color(prev_node["status"]),
                }
                prev_node = node
            # END LOOP

        # END superset_format

        def update_paths(data):
            paths = DBUtils.read_dataset(self.pathing_target_table)
            timeseries = DBUtils.read_dataset(self.timeseries_target_table)

            def fmt_path(path):
                print(path)

                source_measured_status = node_measured_status(data, path["source_id"])
                source_combined_status = node_combined_status(data, path["source_id"])
                target_measured_status = node_measured_status(data, path["target_id"])

                path["source_color"] = fmt_color(source_measured_status)
                path["target_color"] = fmt_color(target_measured_status)
                path["status"] = fmt_status(source_combined_status)
                path["color"] = fmt_color(source_combined_status)

                return path

            # END fmt_path

            def fmt_timeseries(t):
                status = node_combined_status(data, t["id"])
                return {
                    "id": t["id"],
                    "name": t["name"],
                    "status": status,
                    "timestamp": time.time(),
                }

            # END fmt_timeseries

            paths_fmt = [fmt_path(path) for path in paths.to_dict(orient="records")]
            timeseries_fmt = [fmt_timeseries(t) for t in timeseries.to_dict(orient="records")]
            print("insert dataset")
            DBUtils.insert_dataset(
                DataFrame(paths_fmt),
                self.pathing_target_table,
                if_exists=InsertBehavior.REPLACE,
            )
            DBUtils.insert_dataset(
                DataFrame(timeseries_fmt),
                self.timeseries_target_table,
                if_exists=InsertBehavior.APPEND,
            )

        # END update_paths

        if not data_only:
            # Load the model from the repository
            assert isinstance(self.model_options, dict), (
                f"Expected dict for model_options, got {type(self.model_options)}"
            )
            model = ArchimateUtils.load_model_from_repository(
                withData=True, withViews=False, **self.model_options
            )

            # Get the id's of the nodes between which we should calculate the paths
            sources, targets = get_nodes(model)

            # Prepare the model
            prepared_model = prepare_model(model)

            # Calculate the paths
            paths = get_paths(prepared_model, sources, targets)

            # Format the paths
            paths_fmt = DataFrame(
                step for routes in paths for route in routes for step in fmt_path(prepared_model, route)
            )

            if not paths_fmt.empty:
                # Aggregate the paths
                paths_grp = (
                    paths_fmt.groupby(
                        [
                            "source",
                            "source_id",
                            "source_color",
                            "target",
                            "target_id",
                            "target_color",
                            "path_origin",
                            "path_origin_id",
                            "path_destination",
                            "path_destination_id",
                            "status",
                            "color",
                        ]
                    )
                    .size()
                    .reset_index(name="counts")
                )

                # Insert the paths into the database
                DBUtils.insert_dataset(
                    paths_grp,
                    self.pathing_target_table,
                    if_exists=InsertBehavior.REPLACE,
                )

                # Also store the node statuses as time series data
                timeseries_data = DataFrame(
                    [
                        {
                            "id": key,
                            "status": value,
                            "name": fmt_name(prepared_model, key),
                            "timestamp": time.time(),
                        }
                        for key, value in node_status_index.items()
                    ]
                )

                DBUtils.insert_dataset(
                    timeseries_data,
                    self.timeseries_target_table,
                    if_exists=InsertBehavior.APPEND,
                )
            # END IF
        else:
            assert isinstance(self.model_options, dict), (
                f"Expected dict for model_options, got {type(self.model_options)}"
            )
            raw_data = PlatformUtils.retrieve_data(**self.model_options)
            assert raw_data.content is not None, "Expected raw_data.content to be populated"
            data = DataFrame([{"id": content.id, "data": content.data} for content in raw_data.content])
            update_paths(data)
        # END IF

    # END run


# END Pathing
