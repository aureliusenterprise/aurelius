import asyncio
import concurrent
from json import loads
from typing import Dict

from bokeh.embed import json_item
from bokeh.plotting import Figure
from flask import request
from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
  ArchimateUtils
from m4i_analytics.m4i.ApiUtils import ApiUtils
from m4i_analytics.m4i.platform.PlatformApi import PlatformApi
from m4i_metrics.MetricCategory import MetricCategory
from m4i_metrics.MetricConfig import MetricConfig
from m4i_metrics.physical import (DistributionNetworksMetric,
                                  EquipmentAssignedToFacilityMetric,
                                  FacilityRelationsMetric, MaterialFlowMetric,
                                  PhysicalMetric)
from m4i_metrics.process import (ActorAndRoleAssignmentMetric,
                                 EventTriggersProcessMetric,
                                 ExplicitControlFlowMetric,
                                 ProcessBoundariesMetric, ProcessMetric,
                                 ProcessSequenceAndAbstractionMetric)
from m4i_metrics.structural import (ElementsNotInAnyViewMetric,
                                    MissconnectedJunctionsMetric,
                                    StructuralMetric, TreeStructuresMetric,
                                    UnconnectedElementsMetric,
                                    UseOfAssociationRelationsMetric)
from m4i_metrics.textual import (ConceptLabelFormattingMetric,
                                 LabelAndConceptDuplicationMetric,
                                 TextualMetric)
from numpy import nan
from pandas import DataFrame

# This variable defines the structure of the report
report = {
    'Physical Metrics': {
        'Summary': PhysicalMetric.id,
        'Distribution Networks': DistributionNetworksMetric.id,
        'Equipment Assigned to Facility': EquipmentAssignedToFacilityMetric.id,
        'Facility Relations': FacilityRelationsMetric.id,
        'Material Flow': MaterialFlowMetric.id
    },
    'Process Metrics': {
        'Summary':  ProcessMetric.id,
        'Actor & Role Assignment': ActorAndRoleAssignmentMetric.id,
        'Event Triggers Process': EventTriggersProcessMetric.id,
        'Explicit Control Flow': ExplicitControlFlowMetric.id,
        'Process Boundaries': ProcessBoundariesMetric.id,
        'Process Sequence & Abstraction': ProcessSequenceAndAbstractionMetric.id,
    },
    'Structural Metrics': {
        'Summary': StructuralMetric.id,
        'Elements not in any View': ElementsNotInAnyViewMetric.id,
        'Misconnected Junctions': MissconnectedJunctionsMetric.id,
        'Tree Structures': TreeStructuresMetric.id,
        'Unconnected Elements': UnconnectedElementsMetric.id,
        'Use of Association Relations': UseOfAssociationRelationsMetric.id
    },
    'Textual Metrics': {
        'Summary': TextualMetric.id,
        'Concept Label Formatting': ConceptLabelFormattingMetric.id,
        'Label and Concept Duplication': LabelAndConceptDuplicationMetric.id
    }
}

# This dictionary associates every metric with a key from the report structure
metrics = {
    ActorAndRoleAssignmentMetric.id: ActorAndRoleAssignmentMetric,
    ConceptLabelFormattingMetric.id: ConceptLabelFormattingMetric,
    DistributionNetworksMetric.id: DistributionNetworksMetric,
    ElementsNotInAnyViewMetric.id: ElementsNotInAnyViewMetric,
    EquipmentAssignedToFacilityMetric.id: EquipmentAssignedToFacilityMetric,
    EventTriggersProcessMetric.id: EventTriggersProcessMetric,
    ExplicitControlFlowMetric.id: ExplicitControlFlowMetric,
    FacilityRelationsMetric.id: FacilityRelationsMetric,
    LabelAndConceptDuplicationMetric.id: LabelAndConceptDuplicationMetric,
    MaterialFlowMetric.id: MaterialFlowMetric,
    MissconnectedJunctionsMetric.id: MissconnectedJunctionsMetric,
    PhysicalMetric.id: PhysicalMetric,
    ProcessBoundariesMetric.id: ProcessBoundariesMetric,
    ProcessMetric.id: ProcessMetric,
    ProcessSequenceAndAbstractionMetric.id: ProcessSequenceAndAbstractionMetric,
    StructuralMetric.id: StructuralMetric,
    TextualMetric.id: TextualMetric,
    TreeStructuresMetric.id: TreeStructuresMetric,
    UnconnectedElementsMetric.id: UnconnectedElementsMetric,
    UseOfAssociationRelationsMetric.id: UseOfAssociationRelationsMetric
}


def generate_metric(metric_key: str, model_options: dict) -> dict:
    """
    Calculates the metric associated with the given `metric_key` for the model which matches the given `model_options`.

    This is the entry point for the `/metric` route.

    :return: The output of the metric associated with the given key
    :rtype: dict
    """

    if metric_key not in metrics:
        raise ValueError(f'Metric key {metric_key} does not belong to any metric')
    # END IF

    metric = metrics[metric_key]

    '''
    We distinguish between metrics and metric categories, which are aggregates of metrics.
    To calculate a metric category, we make requests to this API to retrieve the submetrics.
    This enables us to use the same cache that is hit by the front-end.
    '''
    if(issubclass(metric, MetricCategory)):
        return _calculate_metric_category(
            metric_category=metric,
            model_options=model_options
        )
    else:
        return _get_metric(
            metric_name=metric_key,
            access_token=model_options['access_token'],
            format_data=False
        )
    # END IF
# END generate_metric


async def calculate_metric(metric_key: str, model_options: dict) -> dict:
    """
    Retrieves the model for the given parameters and resolves the given `metric` based on it.

    This is the entry point for the `/private/metric` route.

    :return: A JSON serializable result for the given Metric
    :rtype: dict
    """

    if metric_key not in metrics:
        raise ValueError(
            f'Metric key {metric_key} does not belong to any metric')
    # END IF

    metric = metrics[metric_key]

    if(issubclass(metric, MetricCategory)):
        raise ValueError(
            'The given metric key belongs to a metric category')
    # END IF

    # Retrieve the model
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:

        def get_model():
            return ArchimateUtils.load_model_from_repository(**model_options)
        # END get_model

        model = await loop.run_in_executor(
            pool,
            get_model
        )
    # END WITH

    # Calculate the metric result
    metric_result = metric.calculate(model)

    # Return a JSON serializable result
    return {
        'type': 'table',
        'data': _format_metric(metric_result)
    }
# END calculate_metric


async def _calculate_metric_category(metric_category: MetricCategory, model_options: dict) -> dict:
    """
    Resolves the given `metric_category`

    :return: A JSON serializable result for the given `metric_category`
    :rtype: dict
    """

    metric_names = [metric.id for metric in metric_category.metrics]

    # Resolve the metrics and exemptions asynchronously
    def resolve_metrics():
        return asyncio.gather(*(
            _get_metric(metric_name, model_options['access_token'])
            for metric_name in metric_names
        ))
    # END resolve_metrics

    def resolve_exemptions():
        return asyncio.gather(*(
            _get_metric_exemptions(
                project_name=model_options['fullProjectName'],
                branch_name=model_options['branchName'],
                version=model_options['version'],
                metric_name=metric_name,
                access_token=model_options['access_token']
            )
            for metric_name in metric_names
        ))
    # END resolve_exceptions

    submetrics, exemptions = await asyncio.gather(
        resolve_metrics(),
        resolve_exemptions()
    )

    summary = metric_category.summarize(
        submetrics,
        exemptions
    )

    # Return a JSON serializable result
    return {
        'type': 'chart',
        'chart': json_item(
            model=_format_chart(
                chart=metric_category.create_graph(summary['Summary']['data'])
            )
        ),
        'data': _format_metric(metric_result=summary),
    }
# END _calculate_metric_category


def _format_chart(chart: Figure) -> Figure:
    """
    Ensures the given `chart` has a responsive layout and does not display the Bokeh logo

    :return: The given `chart` with responsive layout and hidden Bokeh logo
    :rtype: bokeh.plotting.Figure
    """

    chart.sizing_mode = 'stretch_both'
    chart.toolbar.logo = None
    return chart
# END _format_chart


def _format_metric(metric_result: Dict[str, Dict[str, MetricConfig]]) -> dict:
    """
    Turns the given `metric_result` into a JSON serializable format

    :return: A JSON serializable metric result
    :rtype: dict

    :param metric: The metric result that should be formatted
    :type metric: Dict[str, Dict[str, MetricConfig]]
    """

    def fmt_data(data: DataFrame):
        return data.reset_index().reset_index().replace({nan: None}).to_dict(
            orient="records")
    # END fmt_data

    return {
        key: {
            **value,
            'config': value['config'].__dict__(),
            'data': fmt_data(value['data'])
        } for key, value in metric_result.items() if value is not None
    }
# END _format_metric


async def _get_metric_exemptions(project_name: str, branch_name: str, version: int, metric_name: str, access_token: str):
    """
    This function retrieves the exemptions for the project with the given name, branch with the given name, version and metric.

    Because the exemptions api expects a project id and branch id, this function retrieves the project and branch matching the given names first.

    If the lookup fails for whateve reason, returns an empty list.

    :return: A list of exemptions for the given project, branch, version and metric
    :rtype: Sequence[MetricExemption]
    """

    result = []

    project = PlatformApi.retrieve_project(
        project_name, access_token=access_token)

    branches = PlatformApi.get_branches(project.id, access_token=access_token)

    branch_with_name = next(
        (branch for branch in branches if branch.name == branch_name), None)

    if(branch_with_name):

        loop = asyncio.get_event_loop()

        def get_exemptions():
            return PlatformApi.get_metric_exemptions(
                project.id,
                branch_id=branch_with_name.id,
                metric_name=metric_name,
                version=version,
                access_token=access_token
            )
        # END get_exemptions

        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                get_exemptions,
            )
        # END WITH
    # END IF

    return result
# END _get_metric_exemptions


async def _get_metric(metric_name: str, access_token: str, format_data=True) -> dict:
    """
    Retrieves the meric result for the metric with the given name. Makes a local HTTP request to potentially hit the cache.

    :return: The metric result for the metric with the given name as if it was calculated directly by the metric
    :rtype: dict
    """

    # This builds the request url based on path the original call, ensuring the request always makes it to this server
    request_path = f'{request.url_root}private/metric'
    request_args = {**request.args, 'metric': metric_name}

    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor() as pool:

        def get_metric():
            return ApiUtils.get(
                request_path,
                params=request_args,
                access_token=access_token
            )
        # ENd get_metric

        metric = await loop.run_in_executor(
            pool,
            get_metric
        )
    # END WITH

    # Retrieve the metric from the API.
    metric_json = loads(metric)

    if(format_data):
        # Parse the retrieved JSON and format the data of each dataset as a DataFrame
        metric_json = {
            dataset_name: {
                **dataset,
                'data': DataFrame(dataset['data'])
            }
            for dataset_name, dataset in metric_json['data'].items()
        }
    # END IF

    return metric_json
# END _get_metric
