from json import dumps

from flask import Flask, request
from pandas import DataFrame, read_csv, read_excel, read_json
from werkzeug.utils import secure_filename

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
    ArchimateUtils
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import \
    ArchimateModel
from m4i_analytics.graphs.visualisations.LayoutRegistry import LayoutRegistry
from m4i_analytics.model_extractor.ExtractorLanguagePrimitives import (
    ElementDefinition, ExtractorLanguagePrimitives, RelationshipDefinition,
    ViewDefinition)
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.shared import register as register_shared
from m4i_graphviz_layouts import ArchimateHierarchicalLayout, ArchimateProcessLayout

app = Flask(__name__)

# Register the shared core module with the application
register_shared(app)


@app.route('/parse_dataset', methods=['POST'])
#@requires_auth
def parse_dataset(access_token=None):
    """
    Parses a source data file into a set of JSON records. Supports XLS, XLSX, CSV and JSON
    :return: A JSON representation of the source data
    """

    def format_not_supported(f):
        raise ValueError('The provided file format is not supported')
    # END format_not_supported

    if 'multipart/form-data' not in request.content_type:
        raise ValueError('Request Content-Type should be multipart/form-data')
    # END IF

    if 'file' in request.files:
        file = request.files['file']

        filename = secure_filename(file.filename)
        if '.' not in filename:
            raise ValueError('Filename should have an extension')
        # END IF
        extension = filename.rsplit('.', 1)[-1]

        parsers = {
            'xls': read_excel,
            'xlsx': read_excel,
            'csv': read_csv,
            'json': read_json,
        }
        dataframe = parsers.get(extension, format_not_supported)(file)

        return dataframe.to_json(orient='records')
    else:
        raise ValueError('Request payload should contain a part called "file"')
    # END IF
# END parse_dataset


supported_layouts = LayoutRegistry([ArchimateHierarchicalLayout, ArchimateProcessLayout])


@app.route('/extract', methods=['POST'])
#@requires_auth
def extract(access_token=None):
    params = request.get_json()

    data = params.get('data', [])
    rules = params.get('rules', {})

    # Read the given data into a dataframe and create a container model
    dataframe = DataFrame(data)
    model = ArchimateModel('Generated model', defaultAttributeMapping=True)

    # Since the analytics library is agnostic of most layout implementations, check whether the given layout matches any of the ones we know.
    # If the layout is supported, replace the name with the layout instance and add the view to the list we will process further.
    # Otherwise, ignore the view.
    views = rules.get('views', [])
    views_with_layout = []
    for view in views:
        layout = supported_layouts.get_layout(view.get('view_layout'))
        if layout is not None:
            view['view_layout'] = layout
            views_with_layout.append(view)
        # END IF
    # END LOOP

    # Prepare the given rules by passing them into their respective adapters
    element_definitions = [ElementDefinition(
        **el) for el in rules.get('elements', [])]

    # Resolves dependencies to elements
    def fmt_relation(rel):
        source_element = next(
            (element for element in element_definitions if element['id'] == rel['source']), None)
        if source_element is not None:
            rel['source_id_key'] = source_element['id_key']
            rel['source_prefix'] = source_element.get('id_prefix', '')
        # END IF

        target_element = next(
            (element for element in element_definitions if element['id'] == rel['target']), None)
        if target_element:
            rel['target_id_key'] = target_element['id_key']
            rel['target_prefix'] = target_element.get('id_prefix', '')
        # END IF

        return rel
    # END fmt_relation

    relationship_definitions = [RelationshipDefinition(
        **fmt_relation(rel)) for rel in rules.get('relations', [])]

    # Resolves dependencies to elements and relations
    def fmt_view(view):

        def fmt_view_element(element):
            element_ref = next(
                (element_ref for element_ref in element_definitions if element_ref['id'] == element['rule']), None)
            element['id_key'] = element_ref['id_key']
            element['id_prefix'] = element_ref.get('id_prefix', '')
        # END fmt_view_element

        def fmt_view_relation(relation):
            relation_ref = next(
                (relation_ref for relation_ref in relationship_definitions if relation_ref['id'] == relation['rule']), None)
            relation['id_key'] = relation_ref['id_key']
            relation['id_prefix'] = relation_ref.get('id_prefix', '')
        # END fmt_view_relation

        if 'view_nodes' in view:
            for element in view['view_nodes']:
                fmt_view_element(element)
            # END LOOP
        # END IF

        if 'view_edges' in view:
            for relation in view['view_edges']:
                fmt_view_relation(relation)
            # END LOOP
        # END IF

        return view
    # END fmt_view

    view_definitions = [ViewDefinition(**fmt_view(view))
                        for view in views_with_layout]

    # Generate the nodes from the data based on the given definitions and add them to the model
    extracted_elements = ExtractorLanguagePrimitives.parse_concept(
        dataframe, element_definitions, 'Model Extractor API', False)
    nodes_dataframe = DataFrame(list(extracted_elements['nodes']))
    if not nodes_dataframe.empty:
        # Deduplicate only when there are at least 2 rows in the dataframe
        if nodes_dataframe.shape[0] > 1:
            nodes_dataframe.drop_duplicates(
                subset=['id'], keep='last', inplace=True)
        # END IF
        model.nodes = nodes_dataframe
    # END IF

    # Do the same for the edges
    extracted_relations = ExtractorLanguagePrimitives.parse_relationship(
        dataframe, model, relationship_definitions, 'Model Extractor API', False)
    edges_dataframe = DataFrame(list(extracted_relations['edges']))
    if not edges_dataframe.empty:
        # Deduplicate only when there are at least 2 rows in the dataframe
        if edges_dataframe.shape[0] > 1:
            edges_dataframe.drop_duplicates(
                subset=['id'], keep='last', inplace=True)
        # END IF
        model.edges = edges_dataframe
    # END IF

    # Organize the model
    model.organize()

    # Finally, generate the views
    generated_views = ExtractorLanguagePrimitives.parse_view(
        dataframe, model, view_definitions, 'Model Extractor API', False)

    # Return the generated model and metadata
    result = {
        'metadata': list(extracted_elements['metadata']) + list(extracted_relations['metadata']) + list(generated_views['metadata']),
        'model': ArchimateUtils.to_JSON(model)
    }

    return dumps(result)
# END extract
