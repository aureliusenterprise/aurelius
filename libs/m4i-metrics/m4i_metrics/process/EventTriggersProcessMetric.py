import queue
from typing import Any, Dict, List, Tuple

import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

invalid_events_processes_agg_config = MetricConfig(
    description=(
        "These relationships are not triggering between events and processes of the same type. "
        "There are no junctions between the events and processes"
    ),
    id_column="id_rel",
    data={
        "id_rel": MetricColumnConfig(
            displayName="Relationship ID", description="The identifier of the relationship"
        ),
        "type_rel": MetricColumnConfig(
            displayName="Relationship type", description="The type of the relationship"
        ),
        "name_src": MetricColumnConfig(
            displayName="Source name", description="The name of the source element of the relationship"
        ),
        "type_src": MetricColumnConfig(
            displayName="Source type", description="The type of the source element of the relationship"
        ),
        "name_tgt": MetricColumnConfig(
            displayName="Target name", description="The name of the target element of the relationship"
        ),
        "type_tgt": MetricColumnConfig(
            displayName="Target type", description="The type of the target element of the relationship"
        ),
    },
)

invalid_events_junctions_agg_config = MetricConfig(
    description=(
        "These relationships are not triggering between processes and events of the same type. "
        "There are junctions between the events and processes"
    ),
    id_column="id_rel",
    data={
        "id_rel": MetricColumnConfig(
            displayName="Relationship ID", description="The identifier of the relationship"
        ),
        "type_rel": MetricColumnConfig(
            displayName="Relationship type", description="The type of the relationship"
        ),
        "name_start": MetricColumnConfig(
            displayName="Start name",
            description=(
                "The name of the event start/process start of the path of which the relationship is part of"
            ),
        ),
        "type_start": MetricColumnConfig(
            displayName="Start type",
            description=(
                "The type of the event start/process start of the path of which the relationship is part of"
            ),
        ),
        "type_src": MetricColumnConfig(
            displayName="Source type", description="The type of the source element of the relationship"
        ),
        "type_tgt": MetricColumnConfig(
            displayName="Target type", description="The type of the target element of the relationship"
        ),
        "name_end": MetricColumnConfig(
            displayName="End name",
            description=(
                "The name of the event end/process end of the path of which the relationship is part of"
            ),
        ),
        "type_end": MetricColumnConfig(
            displayName="End type",
            description=(
                "The type of the event end/process end of the path of which the relationship is part of"
            ),
        ),
    },
)


def generateinvalidDF_(
    eventtype: str, processtype: str, elems: pd.DataFrame, type_agg: pd.DataFrame
) -> Tuple[int, pd.DataFrame, pd.DataFrame]:
    events_agg: pd.DataFrame = type_agg[  # type: ignore[reportAssignmentType]
        ((type_agg["type_src"] == eventtype) & (type_agg["type_tgt"] == processtype))
        | ((type_agg["type_src"] == processtype) & (type_agg["type_tgt"] == eventtype))
    ]

    invalid_events_agg: pd.DataFrame = events_agg[  # type: ignore[reportAssignmentType]
        events_agg["type_rel"] != RelationshipType.TRIGGERING["typename"]
    ]

    invalid_junction_paths: List[pd.DataFrame] = []
    emptyDF = pd.DataFrame(
        columns=[
            "id_src",
            "type_src",
            "id_rel",
            "type_rel",
            "id_tgt",
            "type_tgt",
            "id_start",
            "name_start",
            "type_start",
            "id_end",
            "name_end",
            "type_end",
        ]
    )
    # avoid ValueError by concat if there is nothing to concatenate
    invalid_junction_paths.append(emptyDF)

    # BFS starts with event, ends with process
    event_agg: pd.DataFrame = elems[elems["type_"] == eventtype]  # type: ignore[reportAssignmentType]
    for _, row in event_agg.iterrows():
        invalid_path_agg: pd.DataFrame = breadth_first_search_(
            row["id"],  # type: ignore[reportArgumentType]
            processtype,
            elems,
            type_agg,  # type: ignore[reportAssignmentType]
        )
        invalid_junction_paths.append(invalid_path_agg)
    # END LOOP

    # BFS starts with process, ends with event
    process_agg: pd.DataFrame = elems[elems["type_"] == processtype]  # type: ignore[reportAssignmentType]
    for _, row in process_agg.iterrows():
        invalid_path_agg = breadth_first_search_(row["id"], eventtype, elems, type_agg)  # type: ignore[reportAssignmentType]
        invalid_junction_paths.append(invalid_path_agg)
    # END LOOP

    junctions_agg: pd.DataFrame = pd.concat(invalid_junction_paths, sort=False)
    junctions_agg.drop_duplicates(inplace=True)
    # turn on subset to also drop duplicates of same relationship ids,
    # but different event_starts/process_starts and process_ends/event_ends

    invalid_junctions_agg = junctions_agg[
        junctions_agg["type_rel"] != RelationshipType.TRIGGERING["typename"]
    ]

    return (
        (len(events_agg) + len(junctions_agg)),
        invalid_events_agg,
        invalid_junctions_agg,  # type: ignore[reportAssignmentType]
    )


# END of generateinvalidDF_


def breadth_first_search_(
    startNodeID: str, endNodeType: str, elems: pd.DataFrame, type_agg: pd.DataFrame
) -> pd.DataFrame:
    visited: List[str] = []
    currentLevel: int = 1
    BFSIDQ: queue.Queue[Tuple[int, str, Dict[int, Dict[str, Any]]]] = queue.Queue(maxsize=0)

    startNodeNeighbours: Dict[str, Dict[str, Any]] = findNeighbours_(startNodeID, type_agg)

    for key_as_ID, value_as_dictEdgeNodes in startNodeNeighbours.items():
        path: Dict[int, Dict[str, Any]] = {}
        path[currentLevel] = value_as_dictEdgeNodes
        BFSIDQ.put((currentLevel, key_as_ID, path))
    # END LOOP

    pathslist: List[pd.DataFrame] = []
    emptyDF: pd.DataFrame = pd.DataFrame(
        columns=[
            "id_src",
            "type_src",
            "id_rel",
            "type_rel",
            "id_tgt",
            "type_tgt",
            "id_start",
            "name_start",
            "type_start",
            "id_end",
            "name_end",
            "type_end",
        ]
    )
    # avoid ValueError by concat if there is nothing to concatenate
    pathslist.append(emptyDF)

    while not BFSIDQ.empty():
        # 3-tuple to track: (depth of node, ID of node,
        # path from startNode to node as a dict. of dictionaries)
        result: Tuple[int, str, Dict[int, Dict[str, Any]]] = BFSIDQ.get()
        levelnumber: int = result[0]
        currentNode: str = result[1]
        path: Dict[int, Dict[str, Any]] = result[2]
        currentLevel: int = levelnumber
        currentNodeType: str = findNodeType_(currentNode, elems)

        if not (
            (currentNodeType == ElementType.AND_JUNCTION["typename"])
            or (currentNodeType == ElementType.OR_JUNCTION["typename"])
        ):
            visited.append(currentNode)

            # path>1 so ending with a path of 1 (no junctions in between) is filtered out
            if (currentNodeType == endNodeType) and len(path) > 1:
                pathsteps: List[Dict[str, Any]] = []
                start_agg: pd.DataFrame = elems[elems["id"] == startNodeID]  # type: ignore[reportAssignmentType]
                end_agg: pd.DataFrame = elems[elems["id"] == currentNode]  # type: ignore[reportAssignmentType]

                for _key, value in path.items():
                    value["id_start"] = start_agg.iloc[0]["id"]
                    value["name_start"] = start_agg.iloc[0]["name"]
                    value["type_start"] = start_agg.iloc[0]["type_"]
                    value["id_end"] = end_agg.iloc[0]["id"]
                    value["name_end"] = end_agg.iloc[0]["name"]
                    value["type_end"] = end_agg.iloc[0]["type_"]
                    # no need to use sorted(dict.items()) in python 3.7+,
                    # keeps insertion order so path uses order of dict insertion without sorted
                    # https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
                    pathsteps.append(value)
                # END LOOP

                pathDF: pd.DataFrame = pd.DataFrame(pathsteps)
                pathslist.append(pathDF)
            else:
                pass
            # END IF
        else:
            if currentNode not in visited:
                visited.append(currentNode)
                currentLevel += 1
                adjacentNodes: Dict[str, Dict[str, Any]] = findNeighbours_(currentNode, type_agg)

                for key_as_ID, value_as_dictEdgeNodes in adjacentNodes.items():
                    # ensure we push unique path dictionaries onto the queue,
                    path = dict(path)

                    # so modifying path doesnt change pushed paths
                    path[currentLevel] = value_as_dictEdgeNodes

                    # add or overwrite when a different node is selected on the same level
                    BFSIDQ.put((currentLevel, key_as_ID, path))
                # END LOOP
            # END IF
        # END IF
    # END LOOP

    paths_df: pd.DataFrame = pd.concat(pathslist, sort=False)
    return paths_df


# END of breadth_first_search_


def findNeighbours_(NodesrcID: str, type_agg: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    # find all neighbours which are a target
    neighbours: Dict[str, Dict[str, Any]] = {}
    adjacent_target_agg: pd.DataFrame = type_agg[type_agg["id_src"] == NodesrcID]  # type: ignore[reportAssignmentType]

    for _row_index, row in adjacent_target_agg.iterrows():
        neighbours[row["id_tgt"]] = {  # type: ignore[reportAssignmentType]
            "id_src": row["id_src"],
            "type_src": row["type_src"],
            "id_rel": row["id_rel"],
            "type_rel": row["type_rel"],
            "id_tgt": row["id_tgt"],
            "type_tgt": row["type_tgt"],
        }
    # END LOOP

    return neighbours


# END of findNeighbours_


def findNodeType_(NodeID: str, elems: pd.DataFrame) -> str:
    NodeID_agg: pd.DataFrame = elems[elems["id"] == NodeID]  # type: ignore[reportAssignmentType]
    return NodeID_agg.iloc[0]["type_"]


# END of findNodeType_


class EventTriggersProcessMetric(Metric):
    id: str = "188b9a34-4a88-45d3-84cd-7f05f48a085c"
    label: str = "Event Triggers Process"

    def calculate(model: Any) -> Dict[str, Any]:  # type: ignore[reportIncompatibleMethodOverride]
        elems: pd.DataFrame = model.nodes.copy()
        elems["type_"] = elems["type"].apply(lambda x: x["typename"])  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
        rels: pd.DataFrame = model.edges.copy()
        rels["type_"] = rels["type"].apply(lambda x: x["typename"])  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]

        elems = elems[["id", "name", "type_"]]  # type: ignore[reportAssignmentType]
        rels = rels[["id", "source", "target", "type_"]]  # type: ignore[reportAssignmentType]

        type_agg: pd.DataFrame = elems.merge(rels, how="inner", left_on="id", right_on="source")
        type_agg.rename(
            columns={
                "id_x": "id_src",
                "name": "name_src",
                "type__x": "type_src",
                "id_y": "id_rel",
                "type__y": "type_rel",
            },
            inplace=True,
        )
        type_agg = type_agg.merge(elems, how="inner", left_on="target", right_on="id")
        type_agg.rename(columns={"id": "id_tgt", "name": "name_tgt", "type_": "type_tgt"}, inplace=True)
        type_agg = type_agg[  # type: ignore[reportAssignmentType]
            ["id_src", "name_src", "type_src", "id_rel", "type_rel", "id_tgt", "name_tgt", "type_tgt"]
        ]

        (businessRels, invalid_business_agg, invalid_business_junction_agg) = generateinvalidDF_(
            ElementType.BUSINESS_EVENT["typename"], ElementType.BUSINESS_PROCESS["typename"], elems, type_agg
        )
        (applicationRels, invalid_application_agg, invalid_application_junction_agg) = generateinvalidDF_(
            ElementType.APPLICATION_EVENT["typename"],
            ElementType.APPLICATION_PROCESS["typename"],
            elems,
            type_agg,
        )
        (technologyRels, invalid_technology_agg, invalid_technology_junction_agg) = generateinvalidDF_(
            ElementType.TECHNOLOGY_EVENT["typename"],
            ElementType.TECHNOLOGY_PROCESS["typename"],
            elems,
            type_agg,
        )

        invalid_events_processes_agg = pd.concat(
            [invalid_business_agg, invalid_application_agg, invalid_technology_agg]
        )

        invalid_events_junctions_agg = pd.concat(
            [invalid_business_junction_agg, invalid_application_junction_agg, invalid_technology_junction_agg]
        )

        invalid_events_junctions_agg = invalid_events_junctions_agg[
            [
                "id_start",
                "name_start",
                "type_start",
                "id_src",
                "type_src",
                "id_rel",
                "type_rel",
                "id_tgt",
                "type_tgt",
                "id_end",
                "name_end",
                "type_end",
            ]
        ]

        allRelsCount = businessRels + applicationRels + technologyRels

        return {
            "Events-processes relationships": {
                "config": invalid_events_processes_agg_config,
                "data": invalid_events_processes_agg,
                "sample_size": allRelsCount,
                "type": "metric",
            },
            "Events-processes relationships with junctions": {
                "config": invalid_events_junctions_agg_config,
                "data": invalid_events_junctions_agg,
                "sample_size": allRelsCount,
                "type": "metric",
            },
        }

    # END of calculate

    def get_name(self):
        return "EventTriggersProcessMetric"

    # END get_name


# END EventTriggersProcessMetric
