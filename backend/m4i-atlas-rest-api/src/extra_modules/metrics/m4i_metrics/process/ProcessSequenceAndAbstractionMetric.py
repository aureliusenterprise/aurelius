import queue

import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

invalid_processes_agg_config = MetricConfig(**{
    'description': 'These relationships are not triggering/aggregation/composition or specialization between similar-type processes. There are no junctions between the processes',
    'id_column': 'id_rel',
    'data': {
        'id_rel': MetricColumnConfig(**{
            'displayName': 'Relationship ID',
            'description': 'The identifier of the relationship'
        }),
        'type_rel': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The type of the relationship'
        }),
        'name_src': MetricColumnConfig(**{
            'displayName': 'Source name',
            'description': 'The name of the source element of the relationship'
        }),
        'type_src': MetricColumnConfig(**{
            'displayName': 'Source type',
            'description': 'The type of the source element of the relationship'
        }),
        'name_tgt': MetricColumnConfig(**{
            'displayName': 'Target name',
            'description': 'The name of the target element of the relationship'
        }),
        'type_tgt': MetricColumnConfig(**{
            'displayName': 'Target type',
            'description': 'The type of the target element of the relationship'
        })
    }
})

invalid_processes_junctions_agg_config = MetricConfig(**{
    'description': 'These relationships are not triggering/aggregation/composition or specialization between similar-type processes. There are junctions between the processes',
    'id_column': 'id_rel',
    'data': {
        'id_rel': MetricColumnConfig(**{
            'displayName': 'Relationship ID',
            'description': 'The identifier of the relationship'
        }),
        'type_rel': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The type of the relationship'
        }),
        'name_start': MetricColumnConfig(**{
            'displayName': 'Start name',
            'description': 'The name of the process start of the path of which the relationship is part of'
        }),
        'type_start': MetricColumnConfig(**{
            'displayName': 'Start type',
            'description': 'The type of the process start of the path of which the relationship is part of'
        }),
        'type_src': MetricColumnConfig(**{
            'displayName': 'Source type',
            'description': 'The type of the source element of the relationship'
        }),
        'type_tgt': MetricColumnConfig(**{
            'displayName': 'Target type',
            'description': 'The type of the target element of the relationship'
        }),
        'name_end': MetricColumnConfig(**{
            'displayName': 'End name',
            'description': 'The name of the process end of the path of which the relationship is part of'
        }),
        'type_end': MetricColumnConfig(**{
            'displayName': 'End type',
            'description': 'The type of the process end of the path of which the relationship is part of'
        })
    }
})


def generateInvalidDF_(processtype, elems, type_agg):

    processes_agg = type_agg[((type_agg['type_src'] == processtype)
                              & (type_agg['type_tgt'] == processtype))]

    invalid_processes_agg = processes_agg[
        ~((processes_agg['type_rel'] == RelationshipType.AGGREGATION['typename'])
          | (processes_agg['type_rel'] == RelationshipType.COMPOSITION['typename'])
          | (processes_agg['type_rel'] == RelationshipType.TRIGGERING['typename'])
          # specialization between similar-type nodes is allowed always
          | (processes_agg['type_rel'] == RelationshipType.SPECIALIZATION['typename']))]

    invalid_junction_paths = []
    emptyDF = pd.DataFrame(columns = ['id_src', 'type_src', 'id_rel', 'type_rel', 'id_tgt',
                                    'type_tgt', 'id_start', 'name_start', 'type_start', 'id_end', 'name_end', 'type_end'])
    # avoid ValueError by concat if there is nothing to concatenate

    invalid_junction_paths.append(emptyDF)
    process_agg = elems[elems['type_'] == processtype]
    for row_index, row in process_agg.iterrows():
        invalid_path_agg = breadth_first_search_(
            row['id'], processtype, elems, type_agg)
        invalid_junction_paths.append(invalid_path_agg)
    # END LOOP

    junctions_agg = pd.concat(invalid_junction_paths, sort=False)
    junctions_agg.drop_duplicates(inplace=True)
    # turn on subset to also drop duplicates of same relationship ids, but different process_starts and process_ends

    invalid_junctions_agg = junctions_agg[junctions_agg['type_rel']
                                          != RelationshipType.TRIGGERING['typename']]

    return ((len(processes_agg) + len(junctions_agg)), invalid_processes_agg, invalid_junctions_agg)
# END of generateinvalidDF_


def breadth_first_search_(startNodeID, endNodeType, elems, type_agg):
    visited = []
    currentLevel = 1
    BFSIDQ = queue.Queue(maxsize=0)

    startNodeNeighbours = findNeighbours_(startNodeID, type_agg)

    for key_as_ID, value_as_dictEdgeNodes in startNodeNeighbours.items():
        path = {}
        path[currentLevel] = value_as_dictEdgeNodes
        BFSIDQ.put((currentLevel, key_as_ID, path))
    # END LOOP

    pathslist = []
    emptyDF = pd.DataFrame(columns = ['id_src', 'type_src', 'id_rel', 'type_rel', 'id_tgt',
                                    'type_tgt', 'id_start', 'name_start', 'type_start', 'id_end', 'name_end', 'type_end'])
    # avoid ValueError by concat if there is nothing to concatenate
    pathslist.append(emptyDF)

    while not BFSIDQ.empty():

        # 3-tuple to track: (depth of node, ID of node,
        # path from startNode to node as a dict. of dictionaries)
        (levelnumber, currentNode, path) = BFSIDQ.get()
        currentLevel = levelnumber
        currentNodeType = findNodeType_(currentNode, elems)

        if not((currentNodeType == ElementType.AND_JUNCTION['typename'])
                or (currentNodeType == ElementType.OR_JUNCTION['typename'])):

            visited.append(currentNode)

            # path>1 so ending with a path of 1 (no junctions in between) is filtered out
            if ((currentNodeType == endNodeType) and len(path) > 1):

                pathsteps = []
                start_agg = elems[elems['id'] == startNodeID]
                end_agg = elems[elems['id'] == currentNode]

                for key, value in path.items():
                    value['id_start'] = start_agg.iloc[0]['id']
                    value['name_start'] = start_agg.iloc[0]['name']
                    value['type_start'] = start_agg.iloc[0]['type_']
                    value['id_end'] = end_agg.iloc[0]['id']
                    value['name_end'] = end_agg.iloc[0]['name']
                    value['type_end'] = end_agg.iloc[0]['type_']
                    # no need to use sorted(dict.items()) in python 3.7+,
                    # keeps insertion order so path uses order of dict insertion without sorted
                    # https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
                    pathsteps.append(value)
                # END LOOP

                pathDF = pd.DataFrame(pathsteps)
                pathslist.append(pathDF)
            else:
                pass
            # END IF
        else:
            if (currentNode not in visited):

                visited.append(currentNode)
                currentLevel += 1
                adjacentNodes = findNeighbours_(currentNode, type_agg)

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

    paths_df = pd.concat(pathslist, sort=False)
    return paths_df
# END of breadth_first_search_


def findNeighbours_(NodesrcID, type_agg):
    # find all neighbours which are a target
    neighbours = {}
    adjacent_target_agg = type_agg[type_agg['id_src'] == NodesrcID]

    for row_index, row in adjacent_target_agg.iterrows():
        neighbours[row['id_tgt']] = {'id_src': row['id_src'], 'type_src': row['type_src'],
                                     'id_rel': row['id_rel'], 'type_rel': row['type_rel'],
                                     'id_tgt': row['id_tgt'], 'type_tgt': row['type_tgt']}
    # END LOOP

    return neighbours
# END of findNeighbours_


def findNodeType_(NodeID, elems):
    NodeID_agg = elems[elems['id'] == NodeID]
    return NodeID_agg.iloc[0]['type_']
# END of findNodeType_


class ProcessSequenceAndAbstractionMetric(Metric):
    id = '71239737-0106-4d0e-838e-7d67f20f42fc'
    label = 'Process Sequence & Abstraction'

    @staticmethod
    def calculate(model):

        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])
        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        elems = elems[['id', 'name', 'type_']]
        rels = rels[['id', 'source', 'target', 'type_']]

        type_agg = elems.merge(
            rels, how='inner', left_on='id', right_on='source')
        type_agg.rename(columns={'id_x': 'id_src', 'name': 'name_src',
                                 'type__x': 'type_src', 'id_y': 'id_rel', 'type__y': 'type_rel'}, inplace=True)
        type_agg = type_agg.merge(
            elems, how='inner', left_on='target', right_on='id')
        type_agg.rename(
            columns={'id': 'id_tgt', 'name': 'name_tgt', 'type_': 'type_tgt'}, inplace=True)
        type_agg = type_agg[['id_src', 'name_src', 'type_src',
                             'id_rel', 'type_rel', 'id_tgt', 'name_tgt', 'type_tgt']]

        businessRels, invalid_business_agg, invalid_business_junction_agg = generateInvalidDF_(
            ElementType.BUSINESS_PROCESS['typename'], elems, type_agg)
        applicationRels, invalid_application_agg, invalid_application_junction_agg = generateInvalidDF_(
            ElementType.APPLICATION_PROCESS['typename'], elems, type_agg)
        technologyRels, invalid_technology_agg, invalid_technology_junction_agg = generateInvalidDF_(
            ElementType.TECHNOLOGY_PROCESS['typename'], elems, type_agg)

        invalid_processes_agg = pd.concat([invalid_business_agg,
                                           invalid_application_agg,
                                           invalid_technology_agg], sort=False)

        invalid_processes_junctions_agg = pd.concat([invalid_business_junction_agg,
                                                     invalid_application_junction_agg,
                                                     invalid_technology_junction_agg], sort=False)
        invalid_processes_junctions_agg = invalid_processes_junctions_agg[[
            'id_start', 'name_start', 'type_start', 'id_src', 'type_src', 'id_rel', 'type_rel', 'id_tgt', 'type_tgt', 'id_end', 'name_end', 'type_end']]

        allRelsCount = businessRels + applicationRels + technologyRels

        return {
            "Relationships between processes": {
                "config": invalid_processes_agg_config,
                "data": invalid_processes_agg,
                "sample_size": allRelsCount,
                "type": "metric"
            },
            "Relationships between processes with junctions": {
                "config": invalid_processes_junctions_agg_config,
                "data": invalid_processes_junctions_agg,
                "sample_size": allRelsCount,
                "type": "metric"
            }
        }
    # END of calculate


    def get_name(self):
        return 'ProcessSequenceAndAbstractionMetric'
    # END get_name

# END ProcessSequenceAndAbstractionMetric