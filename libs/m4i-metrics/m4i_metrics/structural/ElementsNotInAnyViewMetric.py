import itertools

import pandas as pd

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig

hidden_elements_config = MetricConfig(**{
    'description': 'An element is non-compliant if it is present in the model but not present in any ArchiMate Views.',    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the element'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the element'
        }),
        'type_': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'
        })
    }
})


def find_elements_in_view(view):
    """ 
    Yield all elements IDs for an archi View, struct: List of Dictionaries (d)  
    Nested structure, Input format:
        view_parent_nodes = [{'...': '...', 
                            '@elementRef':'id_*', 
                            'ar3_node'= [{ ..<nested_child_nodes>..}]},  
                            { ... }]
    Runs a recursive max depth search, depth determined by presence of the dict key: 'ar3_node'.

    :param list L: archimate View, represented as list of dictionaries, where each dict is a node with poential nested lists with more nodes
    :yields: generator for all nested element ids in the View
    """

    for d in view:
        if d['@xsi_type'] == 'ar3_Element':
            # ensure only elements, and not eg labels get taken into account
            for k, v in d.items():
                if isinstance(v, list) and k == 'ar3_node':
                    # we found a key same name and is a type list
                    for sub_l in find_elements_in_view(v):
                        # continue with the nested child nodes
                        yield sub_l
                    # END LOOP
                elif k == '@elementRef':
                    yield v
                # END IF
            # END LOOP
        # END IF
    # END LOOP
# END find_elements_in_view


class ElementsNotInAnyViewMetric(Metric):
    id = '243c8b8f-921e-4e45-9414-84cf2ec37830'
    label = 'Elements not in any View'

    @staticmethod
    def calculate(model):
        elems = model.nodes.copy()
        elems['type_'] = elems['type'].apply(lambda x: x['typename'])

        elements_in_views = [list(find_elements_in_view(view))
                             for view in model.views.nodes if view is not None]
        # Dijon: skip if view is of type None, edge case; works fine if empty list
        # chose outside the find_* function because type checking inside the
        # function still fails with NoneType object is not iterable
        elements_in_views = list(itertools.chain(*elements_in_views))
        not_in_views = [
            elem_id for elem_id in elems.id if elem_id not in elements_in_views]

        hidden_elements = elems[elems.id.isin(
            not_in_views)][['id', 'name', 'type_']]

        return {
            "elements": {
                "config": hidden_elements_config,
                "data": hidden_elements,
                "sample_size": len(elems.index),
                "type": 'metric'
            }
        }
    # END of calculate

    def get_name(self):
        return 'ElementsNotInAnyViewMetric'
    # END get_name

# END ElementsNotInAnyViewMetric
