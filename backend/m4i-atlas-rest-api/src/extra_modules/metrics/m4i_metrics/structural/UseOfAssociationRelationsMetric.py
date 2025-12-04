import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    ElementType, RelationshipType)

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

invalid_associations_agg_config = MetricConfig(**{
    'description': 'These relationships are association relationships between business layer, application layer, technology layer, physical layer nodes, or junctions.',
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


class UseOfAssociationRelationsMetric(Metric):
    id = '0801347b-5be7-4d3d-88ae-c5bce33619fb'
    label = 'Use of Association Relations'

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

        business_layer = [ElementType.BUSINESS_ACTOR['typename'], ElementType.BUSINESS_ROLE['typename'],
                          ElementType.BUSINESS_COLLABORATION['typename'], ElementType.BUSINESS_INTERFACE['typename'],
                          ElementType.BUSINESS_PROCESS['typename'], ElementType.BUSINESS_FUNCTION['typename'],
                          ElementType.BUSINESS_INTERACTION['typename'], ElementType.BUSINESS_EVENT['typename'],
                          ElementType.BUSINESS_SERVICE['typename'], ElementType.BUSINESS_OBJECT['typename'],
                          ElementType.CONTRACT['typename'], ElementType.REPRESENTATION['typename'],
                          ElementType.PRODUCT['typename']]

        application_layer = [ElementType.APPLICATION_COMPONENT['typename'],
                             ElementType.APPLICATION_COLLABORATION[
                                 'typename'], ElementType.APPLICATION_INTERFACE['typename'],
                             ElementType.APPLICATION_FUNCTION['typename'], ElementType.APPLICATION_INTERACTION['typename'],
                             ElementType.APPLICATION_PROCESS['typename'], ElementType.APPLICATION_EVENT['typename'],
                             ElementType.APPLICATION_SERVICE['typename'], ElementType.DATA_OBJECT['typename']]

        technology_layer = [ElementType.NODE['typename'], ElementType.DEVICE['typename'],
                            ElementType.SYSTEM_SOFTWARE['typename'], ElementType.TECHNOLOGY_COLLABORATION['typename'],
                            ElementType.TECHNOLOGY_INTERFACE['typename'], ElementType.PATH['typename'],
                            ElementType.COMMUNICATION_NETWORK['typename'], ElementType.TECHNOLOGY_FUNCTION['typename'],
                            ElementType.TECHNOLOGY_PROCESS['typename'], ElementType.TECHNOLOGY_INTERACTION['typename'],
                            ElementType.TECHNOLOGY_EVENT['typename'], ElementType.TECHNOLOGY_SERVICE['typename'],
                            ElementType.ARTIFACT['typename']]

        physical_layer = [ElementType.EQUIPMENT['typename'], ElementType.FACILITY['typename'],
                          ElementType.DISTRIBUTION_NETWORK['typename'], ElementType.MATERIAL['typename']]

        junctions = [ElementType.OR_JUNCTION['typename'],
                     ElementType.AND_JUNCTION['typename']]

        all_layers = (business_layer + application_layer +
                      technology_layer + physical_layer + junctions)

        type_agg['SRCinLayers'] = type_agg['type_src'].apply(
            lambda x: x in all_layers)
        type_agg['TGTinLayers'] = type_agg['type_tgt'].apply(
            lambda x: x in all_layers)

        associations_agg = type_agg[type_agg['type_rel']
                                    == RelationshipType.ASSOCIATION['typename']]

        allRelsCount = len(associations_agg)

        invalid_associations_agg = associations_agg[
            (associations_agg['SRCinLayers'] == True) &
            (associations_agg['TGTinLayers'] == True)]
        invalid_associations_agg = invalid_associations_agg[[
            'id_rel', 'type_rel', 'name_src', 'type_src', 'name_tgt', 'type_tgt']]

        return {
            "Cross-layer association relationships": {
                "config": invalid_associations_agg_config,
                "data": invalid_associations_agg,
                "sample_size": allRelsCount,
                "type": 'metric',
            }
        }
    # END of calculate


    def get_name(self):
        return 'UseOfAssociationRelationsMetric'
    # END get_name
    
# END UseOfAssociationRelationsMetric