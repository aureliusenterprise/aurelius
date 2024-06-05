# %%
import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import \
    RelationshipType

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

no_relations_config = MetricConfig(**{
    'description': 'These concepts are nested in a View but do not have a relationship.',
    'id_column': 'concept_id',
    'data': {
        'concept_id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the element'
        }),
        'concept_name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the element'
        }),
        'concept_type': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'
        }),
        'view_name': MetricColumnConfig(**{
            'displayName': 'View name',
            'description': 'The name of the View'
        }),
        'view_path': MetricColumnConfig(**{
            'displayName': 'View Path',
            'description': 'The organizational path of the View'
        })
    }
})

invalid_relations_config = MetricConfig(**{
    'description': 'These concepts are nested in a View but have a relationship that is not allowed. Allowed relationships: Aggregation, Composition, Assignment, and Realization.',
    'id_column': 'concept_id',
    'data': {
        'concept_id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the element'
        }),
        'concept_name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the element'
        }),
        'concept_type': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'
        }),
        'view_name': MetricColumnConfig(**{
            'displayName': 'View name',
            'description': 'The name of the View'
        }),
        'view_path': MetricColumnConfig(**{
            'displayName': 'View Path',
            'description': 'The organizational path of the View'
        }),
        'relation_id': MetricColumnConfig(**{
            'displayName': 'Relationship ID',
            'description': 'The identifier of the relationship'
        }),
        'relation_name': MetricColumnConfig(**{
            'displayName': 'Relationship name',
            'description': 'The name of the relationship'
        }),
        'relation_type': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The ArchiMate type of the relationship'
        })
    }
})


def get_child_parent_pair(nodes, parent=None):
    """
    Returns a flat sequence of tuples representing the given nodes and their direct parents. 
    The returned sequence also includes the children of the given nodes.
    """
    for node in nodes:
        # Continue only if the node is an element
        if '@elementRef' in node:
            node_id = node['@elementRef']
            yield (node_id, parent)
            # If the ar3_node field is present, this node has child nodes
            if 'ar3_node' in node:
                for child_node in get_child_parent_pair(node['ar3_node'], node_id):
                    yield child_node
                # END LOOP
            # END IF
        # END IF
    # END LOOP
# END get_child_parent_pair


def get_view_paths(model):
    # get view names
    # using model.organizations.idRef == model.views.id
    # organizations could be arbitrarily long levels
    view_levels = model.views[['id', 'name']].merge(
        model.organizations, left_on='id', right_on='idRef')
    #  retun  path by concatenating columns with level in their name
    view_levels['path'] = view_levels.loc[:, view_levels.columns.str.contains(
        'level')].apply(lambda x: x.str.cat(sep='/'), 1)
    view_levels = view_levels.rename(columns={'id': 'view_id',
                                              'name': 'view_name',
                                              'path': 'view_path'})
    return view_levels[['view_id', 'view_path', 'view_name']]


def find_nested_elements(model):
    # filter nodes in views that dont nest
        #nested_elems_nodes = [] #
    def filter(view): return [
        dict_elem for dict_elem in view if 'ar3_node' in dict_elem]
    # get all child parent relations for nested elements
    view_nested = {index: get_child_parent_pair(filter(view))
                   for index, view in model.views.nodes.iteritems() if view is not None}

    def remove_top_level_nodes(list_of_tuple): return [
        (x, y) for x, y in list_of_tuple if y != None]
    view_nested = {key: remove_top_level_nodes(
        value) for key, value in view_nested.items()}

    # build dataframe from nested elements
    # for nested elements Archimate requires a proper direction:
    # - source : parent / element with nested elements
    # - target : child / element nested within parent
    # Only testing for the existence of relations from source to target
    rows = []
    for index, pairs in view_nested.items():
        for i in pairs:
            row = model.views.loc[index, ['id']].to_list()+list(i)
            # [view_id, target/child, source/parent]
            rows.append(row)
    return pd.DataFrame.from_records(rows, columns=["view_id", "target", "source"])


def get_elems_rels(model):
    elems = model.nodes.copy()
    elems['type'] = elems['type'].apply(lambda x: x['typename'])
    rels = model.edges.copy()
    rels['type'] = rels['type'].apply(lambda x: x['typename'])
    return elems, rels


class NestedElementsInViewMetric(Metric):
    id = 'd772b9c3-db70-4477-98f1-0fcabf090fb0'
    label = 'Nested Elements in View'

    @staticmethod
    def calculate(model):

        df = find_nested_elements(model)
        elems, rels = get_elems_rels(model)

        if df.empty or elems.empty or rels.empty:
            # Merge fails on empty dataframes
            df_no_relations = pd.DataFrame()
            df_invalid_relations = pd.DataFrame()
        else:
            df = df.merge(rels, how='left', on=['source', 'target'])
            df = df.rename(columns={'id': 'relation_id',
                                    'name': 'relation_name',
                                    'type': 'relation_type'})

            # extend with path names
            path_names = get_view_paths(model)
            df = df.merge(path_names, how='left', on=['view_id'])

            # extend with nested elem data
            df = df.merge(elems, how='left', left_on=[
                          'target'], right_on=['id'])
            df = df.rename(columns={'id': 'concept_id',
                                    'name': 'concept_name',
                                    'type': 'concept_type'})

            allowed_relations = [RelationshipType.COMPOSITION['typename'],
                                 RelationshipType.AGGREGATION['typename'],
                                 RelationshipType.ASSIGNMENT['typename'],
                                 RelationshipType.REALIZATION['typename'],
                                 RelationshipType.SPECIALIZATION['typename'],
                                 ]

            # test compliant conditions
            df_no_relations = df[df['relation_id'].isnull()]
            df = df.dropna()  # remove elements without relations
            df_invalid_relations = df[~df['relation_type'].isin(
                allowed_relations)]

            # select columns to send as payload
            df_no_relations = df_no_relations[['concept_id',
                                               'concept_name',
                                               'concept_type',
                                               'view_name',
                                               'view_path']].reset_index()
            df_invalid_relations = df_invalid_relations[['concept_id',
                                                         'concept_name',
                                                         'concept_type',
                                                         'view_name',
                                                         'view_path',
                                                         'relation_id',
                                                         'relation_name',
                                                         'relation_type']].reset_index()

        return {
            "no relationships": {
                "config": no_relations_config,
                "data": df_no_relations,
                "sample_size": len(df.index),
                "type": 'metric'
            },
            "not allowed relationships": {
                "config": invalid_relations_config,
                "data": df_invalid_relations,
                "sample_size": len(df.index),
                "type": 'metric'
            }
        }
    # END of calculate

    def get_name(self):
        return 'NestedElementsInViewMetric'
    # END get_name
# END NestedElementsInViewMetric
