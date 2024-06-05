import pandas as pd

import m4i_metrics.config as config

from ..Metric import Metric
from ..MetricColumnConfig import MetricColumnConfig
from ..MetricConfig import MetricConfig
from ..utils import MultiMap, index_by_property

copy_non_compliant_config = MetricConfig(**{
    'description': "A concept is non-compliant if it contains the text '(Copy)' in it's label name.",    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the element'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Element name',
            'description': 'The name of the element'
        }),
        'source_type': MetricColumnConfig(**{
            'displayName': 'Element type',
            'description': 'The ArchiMate type of the element'
        })
    }
})


elems_non_compliant_config = MetricConfig(**{
    'description': 'The elements are non-complant if two or more concepts with unique identifiers have the same name and Archimate type.',    'id_column': 'id',
    'data': {
        'id': MetricColumnConfig(**{
            'displayName': 'ID',
            'description': 'The identifier of the concept'
        }),
        'name': MetricColumnConfig(**{
            'displayName': 'Name',
            'description': 'The duplicated name of the concept'
        }),
        'type': MetricColumnConfig(**{
            'displayName': 'Concept type',
            'description': 'The duplicated name of the concept'
        }),
        'cnt': MetricColumnConfig(**{
            'displayName': 'Frequency of the name',
            'description': 'The number of duplicates'
        })
    }
})


rels_non_compliant_config = MetricConfig(**{
    'description': 'The relationships are non-compliant if they are of the same Archimate type and are connecting the same source and target concept.',    'id_column': 'id_relation',
    'data': {
        'id_relation': MetricColumnConfig(**{
            'displayName': 'Relationship ID',
            'description': 'The identifier of the relationship'
        }),
        'type_relation': MetricColumnConfig(**{
            'displayName': 'Relationship type',
            'description': 'The type of the relationship'
        }),
        'name_source': MetricColumnConfig(**{
            'displayName': 'Source element name',
            'description': 'The name of the source element'
        }),
        'name_target': MetricColumnConfig(**{
            'displayName': 'Target element name',
            'description': 'The name of the target element'
        }),
        'cnt': MetricColumnConfig(**{
            'displayName': '# of duplicates',
            'description': 'The number of duplicate relationships between source and target element'
        }),
    }
})


def get_model_copy(model):
    elems = model.nodes.copy()
    rels = model.edges.copy()

    elems['type'] = elems['type'].apply(lambda x: x['typename'])
    rels['type'] = rels['type'].apply(lambda x: x['typename'])
    return elems, rels
# END get_model_copy


def calculate_copy_text(model, elems, rels):
    views = model.views.copy()
    label = 'Copy Text'

    # COPYTEXT
    elems[label] = elems.name.apply(
        lambda x: config.COMPLIANT_TAG if not '(copy)' in x else config.NON_COMPLIANT_TAG)
    rels[label] = rels.name.apply(
        lambda x: config.COMPLIANT_TAG if not '(copy)' in x else config.NON_COMPLIANT_TAG)
    views[label] = views.name.apply(
        lambda x: config.COMPLIANT_TAG if not '(copy)' in x else config.NON_COMPLIANT_TAG)

    elems['source_type'] = 'Element'
    rels['source_type'] = 'Relationship'
    views['source_type'] = 'view'

    copy_non_compliant = pd.concat([elems[elems[label] == config.NON_COMPLIANT_TAG],
                                    rels[rels[label] ==
                                         config.NON_COMPLIANT_TAG],
                                    views[views[label] == config.NON_COMPLIANT_TAG]], sort=False)
    copy_count = len(model.nodes) + \
        len(model.edges)+len(model.views)

    return copy_non_compliant, copy_count
# END calculate_copy_text


def calculate_duplicate_elements(model, elems):
    # remove  default And and OR junctions  labels from being checked
    condition = (elems.name == 'Junction') & (
        (elems.type == 'And Junction') | (elems.type == 'Or Junction'))
    elems = elems.drop(elems[condition].index)

    # create case-insensitive column to groupby
    elems['name_'] = elems['name'].str.lower()
    # duplicate element name and type
    freq_table = elems.groupby(
        ['name_', 'type']).size().rename('cnt').reset_index()
    duplicates = freq_table[freq_table.cnt > 1]
    elems_non_compliant = duplicates.merge(elems, on=['name_', 'type'])[
        ['id', 'name', 'type', 'cnt']]

    elems_count = len(model.nodes)

    return elems_non_compliant, elems_count
# END calculate_duplicate_elements


def calculate_duplicate_relations(model):

    nodes_by_id = index_by_property(
        model.nodes.to_dict(orient='records'),
        'id'
    )

    relationships_by_id = index_by_property(
        model.edges.to_dict(orient='records'),
        'id'
    )

    # Find all relationships of the same type between the same elements 
    duplicate_relations_index = MultiMap()
    for id_, relationship in relationships_by_id.items():
        # The key is composed of the source and target concept ids, and the type of the relationship
        # Use the shorthand type description since it can distinguish easily between different types of access relations
        key = f'{relationship["source"]}-{relationship["target"]}-{relationship["type"]["shorthand"]}'
        duplicate_relations_index.add(key, id_)
    # END LOOP

    # Return all relationships for which another has been found of the same type between the same concepts
    for duplicate_relations in duplicate_relations_index.values():
        duplicates_cnt = len(duplicate_relations)
        if(duplicates_cnt > 1):
            for id_ in duplicate_relations:
                # Look up the relationship for the current id, and its source and target
                relationship = relationships_by_id[id_]
                source = nodes_by_id.get(
                    relationship['source'],
                    relationships_by_id.get(relationship['source'])
                )
                target = nodes_by_id.get(
                    relationship['target'],
                    relationships_by_id.get(relationship['target'])
                )

                # Return a result describing the duplicate relationships
                yield {
                    'id_relation': id_,
                    'type_relation': relationship['type']['typename'],
                    'name_source': source['name'],
                    'name_target': target['name'],
                    'cnt': duplicates_cnt
                }
            # END LOOP
        # END IF
    # END LOOP

    # Finally, return the sample size
    yield len(relationships_by_id)
# END calculate_duplicate_relations


class LabelAndConceptDuplicationMetric(Metric):
    id = '82125c67-f12d-4871-8748-503482ea2acf'
    label = 'Label and Concept Duplication'

    @staticmethod
    def calculate(model):
        elems, rels = get_model_copy(model)
        copy_non_compliant, copy_count = calculate_copy_text(
            model, elems, rels)
        elems_non_compliant, elems_count = calculate_duplicate_elements(
            model, elems)
        *rels_non_compliant, rels_count = calculate_duplicate_relations(
            model
        )

        return {
            "copy text concepts": {
                "config": copy_non_compliant_config,
                "data": copy_non_compliant,
                "sample_size": copy_count,
                "type": 'metric'
            },
            "elements": {
                "config": elems_non_compliant_config,
                "data": elems_non_compliant,
                "sample_size": elems_count,
                "type": 'metric'
            },
            "relationships": {
                "config": rels_non_compliant_config,
                "data": pd.DataFrame(rels_non_compliant),
                "sample_size": rels_count,
                "type": 'metric'
            },
        }
    # END calculate

    def get_name(self):
        return 'LabelAndConceptDuplicationMetric'
    # END get_name

# END LabelAndConceptDuplicationMetric
