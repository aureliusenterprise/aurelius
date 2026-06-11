import numpy as np

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType
from m4i_analytics.m4i.platform.PlatformUtils import PlatformUtils


class PropagationTable:
    """
    This class defines propagation tables that specify which relationships can be
    traversed by the propagation algorithm per source node type.
    """

    DEFAULT = {
        ElementType.BUSINESS_ACTOR: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_ROLE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_COLLABORATION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_INTERFACE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_INTERFACE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_PROCESS: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_FUNCTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_INTERACTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_EVENT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_SERVICE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.BUSINESS_OBJECT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.CONTRACT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.REPRESENTATION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.PRODUCT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_COMPONENT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_COLLABORATION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_INTERFACE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_FUNCTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_FUNCTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_INTERACTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_PROCESS: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_EVENT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.APPLICATION_SERVICE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.DATA_OBJECT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
        ],
        ElementType.NODE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.DEVICE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.SYSTEM_SOFTWARE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_COLLABORATION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_INTERFACE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.PATH: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.COMMUNICATION_NETWORK: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_FUNCTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_PROCESS: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_INTERACTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_EVENT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.TECHNOLOGY_SERVICE: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.ARTIFACT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.EQUIPMENT: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.FACILITY: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.DISTRIBUTION_NETWORK: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.MATERIAL: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.OR_JUNCTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.AND_JUNCTION: [
            RelationshipType.COMPOSITION,
            RelationshipType.AGGREGATION,
            RelationshipType.ASSIGNMENT,
            RelationshipType.REALIZATION,
            RelationshipType.TRIGGERING,
            RelationshipType.FLOW,
            RelationshipType.ACCESS,
            RelationshipType.ACCESS_ACCESS,
            RelationshipType.ACCESS_READ,
            RelationshipType.ACCESS_WRITE,
            RelationshipType.ACCESS_READ_WRITE,
            RelationshipType.SERVING,
            RelationshipType.SPECIALIZATION,
        ],
        ElementType.PLATEAU: [],
    }


# END PropagationTable


def propagate(model_options, propagation_table=PropagationTable.DEFAULT):
    model = ArchimateUtils.load_model_from_repository(userid="propagate", withViews=False, **model_options)

    data = PlatformUtils.retrieve_data(**model_options)
    assert data.content is not None, "Expected data.content to be populated"
    content_list = data.content

    nodes = model.nodes.to_dict(orient="records")

    # Aggregate measured statuses for all nodes and edges
    node_status_agg = {}

    for node in nodes:
        try:
            node_data = next(content.data for content in content_list if content.id == node["id"])
            node_status = node_data["status"]

            result = {
                "data_in": max(node_status[key]["data_in"] for key in node_status),
                "service": max(node_status[key]["service"] for key in node_status),
                "processing": max(node_status[key]["processing"] for key in node_status),
                "data_out": max(node_status[key]["data_out"] for key in node_status),
            }

        except Exception:
            result = {"data_in": 0, "service": 0, "processing": 0, "data_out": 0}

        node_status_agg[node["id"]] = result
    # END LOOP

    # Next, propagate the values measured
    node_status_prop_agg = {}

    def propagate_helper(current_nodes):
        def append(lst, el):
            if not lst:
                lst = []
            lst.append(el)
            return lst

        # END append

        def find_edges(node):
            return model.edges[
                np.logical_and(
                    model.edges.type.isin(propagation_table[node["type"]]),
                    np.logical_or(model.edges.source == node["id"], model.edges.target == node["id"]),
                )
            ].to_dict(orient="records")

        # END find_edges

        propagation_paths = {node["id"]: find_edges(node) for node in current_nodes}

        # Next, propagate all values to the next node. Don't aggregate yet.
        node_status_prop = {}
        for node_id in propagation_paths:
            paths = propagation_paths.get(node_id, [])
            for path in paths:
                # Propagate from the source to the target node, if the target node is not this node
                if path["source"] == node_id:
                    node_status_prop[path["target"]] = append(
                        node_status_prop.get(path["target"]), node_status_agg[node_id]
                    )
                    if node_status_prop_agg.get(node_id):
                        node_status_prop[path["target"]] = append(
                            node_status_prop.get(path["target"]), node_status_prop_agg[node_id]
                        )

                # Access, Aggregation and Composition relations propagate both ways
                elif path["target"] == node_id and path["type"] in [
                    RelationshipType.ACCESS,
                    RelationshipType.ACCESS_ACCESS,
                    RelationshipType.ACCESS_READ,
                    RelationshipType.ACCESS_WRITE,
                    RelationshipType.ACCESS_READ_WRITE,
                ]:
                    node_status_prop[path["source"]] = append(
                        node_status_prop.get(path["source"]), node_status_agg[node_id]
                    )

                    if node_status_prop_agg.get(node_id):
                        node_status_prop[path["source"]] = append(
                            node_status_prop.get(path["source"]), node_status_prop_agg[node_id]
                        )
            # END LOOP
        # END LOOP

        # Next, check whether the new value is higher than the one we already had
        # (both measured and propagated). If so, override the previously propagated
        # value and mark the node as changed.
        changed_nodes = set()
        for node_id in node_status_prop:
            # Make a copy so we can safely manipulate any existing values
            currently_propagated_values = node_status_prop_agg.get(node_id, {}).copy()
            measured_values = node_status_agg.get(node_id, {})

            data_in = max(status.get("data_in", 0) for status in node_status_prop[node_id])
            if data_in > measured_values.get("data_in", 0) and data_in > currently_propagated_values.get(
                "data_in", 0
            ):
                currently_propagated_values["data_in"] = data_in
                changed_nodes.add(node_id)

            service = max(status.get("service", 0) for status in node_status_prop[node_id])
            if service > measured_values.get("service", 0) and service > currently_propagated_values.get(
                "service", 0
            ):
                currently_propagated_values["service"] = service
                changed_nodes.add(node_id)

            processing = max(status.get("processing", 0) for status in node_status_prop[node_id])
            if processing > measured_values.get(
                "processing", 0
            ) and processing > currently_propagated_values.get("processing", 0):
                currently_propagated_values["processing"] = processing
                changed_nodes.add(node_id)

            data_out = max(status.get("data_out", 0) for status in node_status_prop[node_id])
            if data_out > measured_values.get("data_out", 0) and data_out > currently_propagated_values.get(
                "data_out", 0
            ):
                currently_propagated_values["data_out"] = data_out
                changed_nodes.add(node_id)

            # Save any changes
            node_status_prop_agg[node_id] = currently_propagated_values
        # END LOOP

        # Repeat the process for all changed nodes
        if list(changed_nodes):
            propagate_helper([node for node in nodes if node["id"] in list(changed_nodes)])

    # END propagate_helper

    # First propagate all crits
    propagate_helper(
        [
            node
            for node in nodes
            if node["id"] in node_status_agg and max(node_status_agg[node["id"]].values()) == 3
        ]
    )
    # Then all warns
    propagate_helper(
        [
            node
            for node in nodes
            if node["id"] in node_status_agg and max(node_status_agg[node["id"]].values()) == 2
        ]
    )
    # Then all oks
    propagate_helper(
        [
            node
            for node in nodes
            if node["id"] in node_status_agg and max(node_status_agg[node["id"]].values()) == 1
        ]
    )
    # Finally all unks
    # propagate_helper(
    #     [node for node in nodes
    #      if node['id'] in node_status_agg.keys()
    #      and max(node_status_agg[node['id']].values()) == 0]
    # )

    node_data_status_agg = [
        {
            "id": node_id,
            "data": {
                "agg_status": node_status_agg[node_id],
                "measured_data_in": node_status_agg[node_id].get("data_in", 0),
                "measured_service": node_status_agg[node_id].get("service", 0),
                "measured_processing": node_status_agg[node_id].get("processing", 0),
                "measured_data_out": node_status_agg[node_id].get("data_out", 0),
            },
        }
        for node_id in node_status_agg
    ]

    node_data_status_prop_agg = [
        {
            "id": node_id,
            "data": {
                "agg_status_prop": node_status_prop_agg[node_id],
                "propagated_data_in": node_status_prop_agg[node_id].get("data_in", 0),
                "propagated_service": node_status_prop_agg[node_id].get("service", 0),
                "propagated_processing": node_status_prop_agg[node_id].get("processing", 0),
                "propagated_data_out": node_status_prop_agg[node_id].get("data_out", 0),
            },
        }
        for node_id in node_status_prop_agg
    ]

    def combine_status(node_id):
        own_status = next(
            (node["data"].get("agg_status", {}) for node in node_data_status_agg if node["id"] == node_id), {}
        )
        prop_status = next(
            (
                node["data"].get("agg_status_prop", {})
                for node in node_data_status_prop_agg
                if node["id"] == node_id
            ),
            {},
        )

        own_data_in = own_status.get("data_in", 0)
        prop_data_in = prop_status.get("data_in", 0)

        own_service = own_status.get("service", 0)
        prop_service = prop_status.get("service", 0)

        own_processing = own_status.get("processing", 0)
        prop_processing = prop_status.get("processing", 0)

        own_data_out = own_status.get("data_out", 0)
        prop_data_out = prop_status.get("data_out", 0)

        result = {
            "combined_data_in": max(own_data_in, prop_data_in),
            "combined_service": max(own_service, prop_service),
            "combined_processing": max(own_processing, prop_processing),
            "combined_data_out": max(own_data_out, prop_data_out),
        }

        return result

    # END combine_status

    node_data_status_comb = [{"id": node["id"], "data": combine_status(node["id"])} for node in nodes]

    def merge_dicts(a, b):
        def merge(dict1, dict2):
            for k in set(list(dict1.keys())) | set(list(dict2.keys())):
                if k in dict1 and k in dict2:
                    if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                        yield k, merge_dicts(dict1[k], dict2[k])
                    else:
                        yield k, dict2[k]
                elif k in dict1:
                    yield k, dict1[k]
                else:
                    yield k, dict2[k]

        # END merge
        if len(a) == 0:
            return b
        elif len(b) == 0:
            return a
        else:
            return dict(merge(a, b))

    # END merge_dicts

    all_data = []
    id_mapping = {}

    for el in node_data_status_agg:
        id_mapping[el["id"]] = (
            id_mapping[el["id"]] + [el["data"]] if id_mapping.get(el["id"]) else [el["data"]]
        )
    # END LOOP

    for el in node_data_status_prop_agg:
        id_mapping[el["id"]] = (
            id_mapping[el["id"]] + [el["data"]] if id_mapping.get(el["id"]) else [el["data"]]
        )
    # END LOOP

    for el in node_data_status_comb:
        id_mapping[el["id"]] = (
            id_mapping[el["id"]] + [el["data"]] if id_mapping.get(el["id"]) else [el["data"]]
        )
    # END LOOP

    for key in id_mapping:
        dicts = iter(id_mapping[key])
        result = next(dicts)
        for curr in dicts:
            result = merge_dicts(result, curr)
        # END LOOP
        all_data.append({"id": key, "data": result})
    # END LOOP

    return all_data


# END propagate
