from typing import Iterable, Tuple
from uuid import uuid4 as uuid

from numpy import nan
from pandas import DataFrame, concat

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
  ArchimateUtils
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import \
  ArchimateModel
from m4i_backend_core.utils import index_by_property


def compare_concepts(source_concepts: Iterable[dict], target_concepts: Iterable[dict], id_key: str = 'id', view_elements: bool = False) -> Iterable[Tuple[str, str]]:
    """
    Compare the given sets of concepts. 
    Concepts are matched by the given `id_key`. 
    Differences are classified as either 'added', 'removed', 'unchanged' or 'changed'.

    :returns: The differences found as a tuple of the concept id and the difference classification.
    :rtype: Iterable[Tuple[str, str]]

    :param Iterable[dict] source_concepts: The concepts from the source model that should be compared
    :param Iterable[dict] target_concepts: The concepts from the target model that should be compared
    :param str id_key: The name of the property that contains the id of the given concepts
    :param bool view_elements: Whether or not the given concepts are view elements (as opposed to concepts from the model)
    """

    def is_concept_changed(source_concept: dict, target_concept: dict) -> bool:
        """
        Returns whether or not a change has occurred between the given concepts.
        A concept is considered changed if any of its fields differ (this also includes nested fields).

        :returns: Whether or not a change has occurred between the given concepts.
        :rtype: bool

        :param dict source_concept: The base concept
        :param dict target_concept: The concept to compare against the base concept
        """
        return source_concept != target_concept
    # END is_concept_changed

    # Index the concepts in the source and target models by ID
    source_concepts_by_id = index_by_property(source_concepts, id_key)
    target_concepts_by_id = index_by_property(target_concepts, id_key)

    # Retrieve the ids of the concepts that are in both the source and target models by taking the keys of the respective indices
    source_ids = source_concepts_by_id.keys()
    target_ids = target_concepts_by_id.keys()

    # A concept is in both the source and target model if its ID is present in both indices
    shared_ids = source_ids & target_ids

    # Derive the concepts that are only in the source or target models by taking the difference of the ids in the respectrive indices and the shared ids
    source_only = source_ids - shared_ids
    target_only = target_ids - shared_ids

    # Return which elements were added, removed, changed or unchanged as a flat list
    for id_ in source_only:
        yield (id_, 'model 1 view only' if view_elements else 'model 1 only')
    # END LOOP

    for id_ in target_only:
        yield (id_, 'model 2 view only' if view_elements else 'model 2 only')
    # END LOOP

    for id_ in shared_ids:
        source_concept = source_concepts_by_id[id_]
        target_concept = target_concepts_by_id[id_]

        if is_concept_changed(source_concept, target_concept):
            yield (id_, 'changed in view' if view_elements else 'changed')
        # END IF
        else:
            yield (id_, 'unchanged')
    # END LOOP
# END compare_nodes


def compare_view_contents(source_views: Iterable[dict], target_views: Iterable[dict]) -> Iterable[Tuple[str, str]]:
    """
    For the given sets of views, compare the contents of views with matching ids. Differences are classified as either 'added', 'removed', 'unchanged' or 'changed'.

    :returns: The differences found as a tuple of the view element id and the difference classification.
    :rtype: Iterable[Tuple[str, str]]

    :param Iterable[dict] source_views: The views from the source model that should be compared
    :param Iterable[dict] target_views: The views from the target model that should be compared
    """

    def compare_view_elements(source_view_elements: Iterable[dict], target_view_elements: Iterable[dict]) -> Iterable[Tuple[str, str]]:
        """
        Compare the contents of a single view. 
        Returns a set of differences for the given elements.
        This function works for nodes as well as connections. 

        :returns: A set of differences for the given elements.
        :rtype: Iterable[Tuple[str, str]]

        :param Iterable[dict] source_view_elements: The contents of the base view
        :param Iterable[dict] target_view_elements: The contents of the view that should be compared against the base view
        """
        # Flatten the list of view elements to include nested nodes
        flat_source_elements = ArchimateUtils.get_view_nodes(
            source_view_elements
        ) if source_view_elements is not None else []

        flat_target_elements = ArchimateUtils.get_view_nodes(
            target_view_elements
        ) if target_view_elements is not None else []

        return compare_concepts(
            source_concepts=flat_source_elements,
            target_concepts=flat_target_elements,
            id_key='@identifier',
            view_elements=True
        )
    # END compare_view_nodes

    # Index the views in the source and target models by ID
    source_views_by_id = index_by_property(
        data=source_views,
        property_name='id'
    )

    target_views_by_id = index_by_property(
        data=target_views,
        property_name='id'
    )

    # Retrieve the ids of the elements that are in both the source and target views by taking the keys of the respective indices
    source_ids = source_views_by_id.keys()
    target_ids = target_views_by_id.keys()

    # A concept is in both the source and target views if its ID is present in both indices
    shared_ids = source_ids & target_ids

    # Only determine the differences for views that are in both models
    for id_ in shared_ids:

        source_view = source_views_by_id[id_]
        target_view = target_views_by_id[id_]

        node_differences = compare_view_elements(
            source_view_elements=source_view['nodes'],
            target_view_elements=target_view['nodes']
        )

        for difference in node_differences:
            yield difference
        # END LOOP

        edge_differences = compare_view_elements(
            source_view_elements=source_view['connections'],
            target_view_elements=target_view['connections']
        )

        for difference in edge_differences:
            yield difference
        # END LOOP
    # END LOOP
# END compare_view_contents


def merge_models(source_model: ArchimateModel, target_model: ArchimateModel, model_differences: Iterable[Tuple[dict, dict]]) -> Tuple[ArchimateModel, dict]:
    """
    Combines the two given models into a single model.
    Elements which occur in both models, and for which a change is found, are duplicated and assigned a new id.
    Returns the merged model, as well as a mapping of the original and newly assigned concept ids.

    :returns: The merged model, as well as a mapping of the original and newly assigned concept ids.
    :rtype: Tuple[ArchimateModel, dict]

    :param ArchimateModel source_model: The base model
    :param ArchimateModel target_model: The model that was compared against the base model
    :param Iterable[Tuple[str, str]] model_differences: A set of differences represented by the id of a concept in the model, and a classification of the difference.
    """

    # Keep a record of all the ids we've replaced for future reference
    id_mapping = {}

    def get_replacement_id(id_: str) -> str:
        """
        Returns a replacement id for the given id.
        For any single given id, always returns the same replacement id.
        Also ensures an entry is made into the global id mapping.

        :returns: A replacement id for the given id.
        :rtype: str

        :param str id_: The id that needs to be replaced 
        """

        # If the given id already exists in the mapping, return the previously generated id
        if id_ in id_mapping:
            return id_mapping[id_]
        # END IF

        # Otherwise, create a new replacement id and add it to the mapping before returning it
        replacement_id = f'{id_}_model_2'
        id_mapping[id_] = replacement_id
        return replacement_id
    # END get_replacement_id

    def replace_view_element_id(view_element: dict) -> dict:
        """
        Replaces the id of the given view element, as well as any child elements

        :returns: The view element with its id replaced
        :rtype: dict

        :param dict view_element: The view element for which the id should be replaced
        """
        def replace_child_element_ids() -> Iterable[dict]:
            """
            Replaces the ids of any child elements.

            :returns: The child elements with their ids replaced.
            :rtype: Iterable[dict]
            """
            if('ar3_node' in view_element):
                children = view_element['ar3_node']
                for child in children:
                    yield replace_view_element_id(child)
                # END LOOP
            # END IF
        # END replace_child_element_ids

        updated_element = {
            **view_element,
            '@identifier': get_replacement_id(view_element['@identifier']),\
            # Also replace the ids of any child elements
            'ar3_node': list(replace_child_element_ids())
        }

        return updated_element
    # END replace_view_element_ids

    def replace_view_connection_source_and_target_ids(view_connection: dict) -> dict:
        """
        Ensures the source and target of the given connection reflect the updated ids

        :returns: The given connection with with updated source and target.
        :rtype: dict

        :param dict view_connection: The view connection for which the source and target should be updated
        """
        updated_connection = {
            **view_connection,
            '@source': get_replacement_id(view_connection['@source']),
            '@target': get_replacement_id(view_connection['@target'])
        }
        return updated_connection
    # END replace_view_connection_source_and_target_ids

    def replace_view_content_ids(view: dict) -> dict:
        """
        Replaces the ids of all nodes and connections in the given view.
        Replaced ids are added to the global id mapping.

        :returns: The given view with the ids of its nodes and connections updated
        :rtype: dict

        :param dict view: The view for which the ids of its nodes and edges should be updated
        """
        # Replace the base ids of the nodes and connections in the view
        nodes = map(replace_view_element_id, view['nodes'])
        connections_with_updated_ids = map(
            replace_view_element_id,
            view['connections']
        )
        # Replace the sources and targets of the view connections after replacing the base ids to account for relations to relations
        connections_with_updated_source_and_target = map(
            replace_view_connection_source_and_target_ids,
            connections_with_updated_ids
        )

        updated_view = {
            **view,
            'nodes': list(nodes),
            'connections': list(connections_with_updated_source_and_target)
        }

        return updated_view
    # END replace_view_content_ids

    # For all changed elements, the IDs need to be replaced in the target model, so we can keep both the source and target versions in the merged model
    # Rather than traverse the model as a datastructure, convert the model to a json string and replace the id of the changed element wherever it occurs
    target_model_json = ArchimateUtils.to_JSON(target_model)

    for id_, difference in model_differences:
        if difference == 'changed':
            target_model_json = target_model_json.replace(
                id_,
                get_replacement_id(id_)
            )
        # END IF
    # END LOOP

    # Convert the json string with the updated IDs back into a model
    target_model_with_updated_ids = ArchimateUtils.load_model(
        target_model_json
    )

    # Replace the ids of all view elements to avoid a bug in Archi
    target_views_with_updated_content_ids = map(
        replace_view_content_ids,
        target_model_with_updated_ids.views.to_dict(orient='records')
    )
    target_model_with_updated_ids.views = DataFrame(
        target_views_with_updated_content_ids
    )

    # Merge the nodes, edges, views and organizations of the source and updated target model
    merged_nodes = concat([
        source_model.nodes,
        target_model_with_updated_ids.nodes
    ]).drop_duplicates(subset='id')

    merged_edges = concat([
        source_model.edges,
        target_model_with_updated_ids.edges
    ]).drop_duplicates(subset='id')

    merged_views = concat([
        source_model.views,
        target_model_with_updated_ids.views
    ]).drop_duplicates(subset='id')

    merged_organizations = concat([
        source_model.organizations,
        target_model_with_updated_ids.organizations
    ]).drop_duplicates(subset='idRef')

    # Create a new model with the merged content
    merged_model = ArchimateModel(
        name=f'Model combining \'{source_model.name}\' and \'{target_model.name}\'',
        nodes=merged_nodes,
        edges=merged_edges,
        views=merged_views,
        organizations=merged_organizations,
        defaultAttributeMapping=True
    )

    return merged_model, id_mapping
# END merge_models


def add_difference_folders_to_organizations(model: ArchimateModel, model_differences: Iterable[Tuple[str, str]], id_mapping: dict) -> ArchimateModel:
    """
    Adds folders to the organization of the given model to reflect the given model differences. 
    Concepts are placed in folders called 'added', 'removed', 'unchanged' or 'changed', respective of the differences found.
    If a concept was changed, include the concept from the source model in a subfolder called 'source', and the concept from the target model in a subfolder called 'target'.

    :returns: The given model with an updated folder structure
    :rtype: ArchimateModel

    :params ArchimateModel model: The model for which to update the folder sturcture
    :param Iterable[Tuple[str, str]] model_differences: A set of differences represented by the id of a concept in the model, and a classification of the difference.
    :param id_mapping: A lookup table of original and replacement ids, generated when merging the source and target models.
    """

    organizations_by_idref = index_by_property(
        data=model.organizations.to_dict(orient='records'),
        property_name='idRef'
    )

    def map_concepts_to_difference_folders() -> Iterable[dict]:
        """
        Generates the folder structure based on the given set of differences

        :returns: The updated organizations of the model
        :rtype: Iterable[dict]
        """
        for id_, difference in model_differences:

            # Stupid dataframe adds None columns to the dictionary.
            # This can artificially inflate the folder depth.
            # So filter out all kv-pairs that have a value of None.
            current_folder_structure = {
                key: value
                for key, value in organizations_by_idref[id_].items()
                if value is not None
            }

            depth = len(current_folder_structure)

            # In case of a modification, we want to show the original and the updated version of the concept in separate folders
            # Otherwise (in case of an addition, removal or no change), we only need to include one version of the concept
            if(difference == 'changed'):
                source_folder_structure = {
                    **current_folder_structure,
                    f'level{depth}': difference,
                    f'level{depth + 1}': 'model 1',
                    f'level{depth + 2}': None
                }
                target_folder_structure = {
                    **current_folder_structure,
                    'idRef': id_mapping[id_],
                    f'level{depth}': difference,
                    f'level{depth + 1}': 'model 2',
                    f'level{depth + 2}': None
                }
                yield source_folder_structure
                yield target_folder_structure
            else:
                updated_folder_structure = {
                    **current_folder_structure,
                    f'level{depth}': difference,
                    f'level{depth + 1}': None
                }
                yield updated_folder_structure
            # END IF
        # END LOOP
    # END add_difference_folder

    # Replace any potential NaN columns in the DataFrame with None
    organizations_with_difference_folders = DataFrame(
        map_concepts_to_difference_folders()
    ).replace({nan: None})

    model.organizations = organizations_with_difference_folders

    return model
# END add_difference_folders_to_organizations


def map_difference_ids(differences: Iterable[Tuple[str, str]], id_mapping: dict) -> Iterable[Tuple[str, str]]:
    """
    Maps the ids of the given differences agains the given id map. 
    If an id mapping is found for a given difference, include a difference for both the original id as well as the mapped id.

    :returns: A set of differences that reflect both the original and the mapped ids.
    :rtype: Iterable[Tuple[str, str]]

    :param Iterable[Tuple[str, str]] differences: A set of differences represented by the id of a concept in the model, and a classification of the difference.
    :param id_mapping: A lookup table of original and replacement ids, generated when merging the source and target models.
    """
    for id_, difference in differences:
        yield (id_, difference)
        if id_ in id_mapping:
            yield (id_mapping[id_], difference)
        # END IF
    # END LOOP
# END map_difference_ids


def compare_models(source_model: ArchimateModel, target_model: ArchimateModel) -> Tuple[Iterable[Tuple[str, str]], ArchimateModel]:
    """
    Compares the given models by nodes, edges, views and view contents. 
    Returns the differences found, as well as a model that combines the source and target model to reflect the differences found.
    The combined model can e.g. be used for a color view.

    :returns: The differences found, as well as a model that combines the source and target model to reflect the differences found.
    :rtype: Tuple[Iterable[Tuple[str, str]], ArchimateModel]

    :param ArchimateModel source_model: The base model
    :param ArchimateModel target_model: The model to compare against the base model
    """

    # Start by comparing the elements, relationshps and views in the model
    node_differences = compare_concepts(
        source_concepts=source_model.nodes.to_dict(orient='records'),
        target_concepts=target_model.nodes.to_dict(orient='records')
    )

    edge_differences = compare_concepts(
        source_concepts=source_model.edges.to_dict(orient='records'),
        target_concepts=target_model.edges.to_dict(orient='records')
    )

    source_views = source_model.views.to_dict(orient='records')
    target_views = target_model.views.to_dict(orient='records')

    view_differences = compare_concepts(
        source_concepts=source_views,
        target_concepts=target_views
    )

    # Also compare the contents of the views for visual changes
    view_content_differences = compare_view_contents(
        source_views=source_views,
        target_views=target_views
    )

    # Merge the source and target models.
    # For changed elements that exist in both the source and target models, both versions are kept.
    # In this case, one of the elements must be assigned a new ID
    # The returned ID mapping contains, for every reasssigned ID, the original and the new value
    model_differences = [
        *node_differences,
        *edge_differences,
        *view_differences
    ]

    merged_model, id_mapping = merge_models(
        source_model=source_model,
        target_model=target_model,
        model_differences=model_differences
    )

    # Ensure that the differences found reflect the reassigned ids.
    differences = map_difference_ids(
        differences=(*model_differences, *view_content_differences),
        id_mapping=id_mapping
    )

    # Change the folder structure such that concepts are categorized as added, removed, changed or unchanged
    merged_model_with_difference_folders = add_difference_folders_to_organizations(
        model=merged_model,
        model_differences=model_differences,
        id_mapping=id_mapping
    )

    # Return the differences and the merged model
    return differences, merged_model_with_difference_folders
# END compare_models
