import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from m4i_metrics.Metric import Metric
from m4i_metrics.MetricColumnConfig import MetricColumnConfig
from m4i_metrics.MetricConfig import MetricConfig

invalid_actors_roles_processes_functions_agg_config = MetricConfig(**{
    'description': 'These relationships are not assignment between business actors and business roles or business actors/business roles and business processes/business functions',
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


class ActorAndRoleAssignmentMetric(Metric):
    id = '32e068fe-973b-4b9a-982b-5eea2a70b2d7'
    label = 'Actor & Role Assignment'

    @staticmethod
    def calculate(model):
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])
        rels = model.edges.copy()
        rels['type_'] = rels['type'].apply(lambda x: x['typename'])

        elems = elems[['id', 'name', 'type_']]
        rels = rels[['id', 'source', 'target', 'type_']]

        business_elems = elems[
            (elems['type_'] == ElementType.BUSINESS_ACTOR['typename'])
            | (elems['type_'] == ElementType.BUSINESS_ROLE['typename'])
            | (elems['type_'] == ElementType.BUSINESS_PROCESS['typename'])
            | (elems['type_'] == ElementType.BUSINESS_FUNCTION['typename'])]

        business_agg = business_elems.merge(
            rels, how='inner', left_on='id', right_on='source')
        business_agg.rename(columns={'id_x': 'id_src', 'name': 'name_src',
                                     'type__x': 'type_src', 'id_y': 'id_rel', 'type__y': 'type_rel'}, inplace=True)
        business_agg = business_agg.merge(
            business_elems, how='inner', left_on='target', right_on='id')
        business_agg.rename(
            columns={'id': 'id_tgt', 'name': 'name_tgt', 'type_': 'type_tgt'}, inplace=True)
        business_agg = business_agg[['id_src', 'name_src', 'type_src',
                                     'id_rel', 'type_rel', 'id_tgt', 'name_tgt', 'type_tgt']]

        # these 5 relationship-checks go one direction only,
        # because assignment is only possible using this direction in Archi
        actors_roles_agg = business_agg[(
            (business_agg['type_src'] == ElementType.BUSINESS_ACTOR['typename']) &
            (business_agg['type_tgt'] == ElementType.BUSINESS_ROLE['typename']))]

        actors_processes_agg = business_agg[(
            (business_agg['type_src'] == ElementType.BUSINESS_ACTOR['typename']) &
            (business_agg['type_tgt'] == ElementType.BUSINESS_PROCESS['typename']))]

        roles_processes_agg = business_agg[(
            (business_agg['type_src'] == ElementType.BUSINESS_ROLE['typename']) &
            (business_agg['type_tgt'] == ElementType.BUSINESS_PROCESS['typename']))]

        actors_functions_agg = business_agg[(
            (business_agg['type_src'] == ElementType.BUSINESS_ACTOR['typename']) &
            (business_agg['type_tgt'] == ElementType.BUSINESS_FUNCTION['typename']))]

        roles_functions_agg = business_agg[(
            (business_agg['type_src'] == ElementType.BUSINESS_ROLE['typename']) &
            (business_agg['type_tgt'] == ElementType.BUSINESS_FUNCTION['typename']))]

        actors_roles_processes_functions_agg = pd.concat(
            [actors_roles_agg, actors_processes_agg, roles_processes_agg,
             actors_functions_agg, roles_functions_agg])
             
        allRelsCount = len(actors_roles_processes_functions_agg)

        invalid_actors_roles_processes_functions_agg = actors_roles_processes_functions_agg[
            actors_roles_processes_functions_agg['type_rel'] != RelationshipType.ASSIGNMENT['typename']]

        return {
            "Relationships between business actors, business roles, business processes and business functions": {
                "config": invalid_actors_roles_processes_functions_agg_config,
                "data": invalid_actors_roles_processes_functions_agg,
                "sample_size": allRelsCount,
                "type": "metric"
            }
        }
    # END of calculate


    def get_name(self):
        return 'ActorAndRoleAssignmentMetric'
    # END get_name

# END ActorAndRoleAssignmentMetric
