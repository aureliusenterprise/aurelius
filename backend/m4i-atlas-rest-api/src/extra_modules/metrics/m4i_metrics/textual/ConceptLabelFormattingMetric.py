import re

import pandas as pd

import m4i_metrics.config as config

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

elems_non_compliant_config = MetricConfig(**{
    'description': 'The names of these elements are not structured as a sentence',
    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the element'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Current name',
            'description': 'The current name of the element'
        }),
        'rec_name': MetricColumnConfig(**{
            'displayName': 'Suggested name',
            'description': 'The suggested name of the element'
        })
    }
})

rels_non_compliant_config = MetricConfig(**{
    'description': 'The names of these relationships are not structured as a sentence',
    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the relationship'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Current name',
            'description': 'The current name of the relationship'
        }),
        'rec_name': MetricColumnConfig(**{
            'displayName': 'Suggested name',
            'description': 'The suggested name of the relationship'
        })
    }
})

views_non_compliant_config = MetricConfig(**{
    'description': 'The names of these views are not structured as a sentence',
    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the view'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Current name',
            'description': 'The current name of the view'
        }),
        'rec_name': MetricColumnConfig(**{
            'displayName': 'Suggested name',
            'description': 'The suggested name of the view'
        })
    }
})

sentence = re.compile(
    r"^[A-Z1-90][a-zA-Z1-90\.\-_\(\)\[\])]*([ ][A-Za-z1-90\(\)\[\]][a-zA-Z1-90\.\-_\(\)\[\])]*|$)*$"
)


class ConceptLabelFormattingMetric(Metric):
    id = '8ddd174e-0c42-478b-b719-8d678a72304f'
    label = 'Concept Label Formatting'

    @staticmethod
    def calculate(model):

        elems = model.nodes.copy()
        rels = model.edges.copy()
        views = model.views.copy()

        elems['sentence'] = elems.name.apply(lambda x: config.COMPLIANT_TAG if not sentence.match(
            x) == None else config.NON_COMPLIANT_TAG)
        rels['sentence'] = rels.name.apply(lambda x: config.COMPLIANT_TAG if x in [
                                           'Yes', 'No'] or x is None or len(x) == 0 else config.NON_COMPLIANT_TAG)
        views['sentence'] = views.name.apply(lambda x: config.COMPLIANT_TAG if not sentence.match(
            x) == None else config.NON_COMPLIANT_TAG)
        elems['rec_name'] = elems.name.apply(
            lambda x: x.capitalize() if sentence.match(x.capitalize()) else '')
        rels['rec_name'] = rels.name.apply(
            lambda x: x.capitalize() if x.capitalize() in ['Yes', 'No'] else '')
        views['rec_name'] = views.name.apply(
            lambda x: x.capitalize() if sentence.match(x.capitalize()) else '')

        elems_non_compliant = elems[elems.sentence == config.NON_COMPLIANT_TAG][[
            'id', 'name', 'rec_name']]
        rels_non_compliant = rels[rels.sentence == config.NON_COMPLIANT_TAG][[
            'id', 'name', 'rec_name']]
        views_non_compliant = views[views.sentence == config.NON_COMPLIANT_TAG][[
            'id', 'name', 'rec_name']]

        return {
            "elements": {
                "config": elems_non_compliant_config,
                "data": elems_non_compliant,
                "sample_size": len(elems.index),
                "type": 'metric'
            },
            "relationships": {
                "config": rels_non_compliant_config,
                "data": rels_non_compliant,
                "sample_size": len(rels.index),
                "type": 'metric'
            },
            "views": {
                "config": views_non_compliant_config,
                "data": views_non_compliant,
                "sample_size": len(views.index),
                "type": 'metric'
            }
        }
    # END of calculate

    def get_name(self):
        return 'ConceptLabelFormattingMetric'
    # END get_name
# END ConceptLabelFormattingMetric
