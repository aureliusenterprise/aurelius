# -*- coding: utf-8 -*-

from bokeh.io import output_file, show
from bokeh.layouts import layout, widgetbox
from bokeh.models import Panel
from bokeh.models.widgets import Div, Tabs

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import \
    ArchimateUtils
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import \
    ArchimateModel
from m4i_analytics.m4i.platform.PlatformApi import PlatformApi
from m4i_metrics.html_report.create_metric_grid import create_metric_grid
from m4i_metrics.Metric import Metric
from m4i_metrics.MetricCategory import MetricCategory
from m4i_metrics.process.ProcessMetric import ProcessMetric
from m4i_metrics.structural.StructuralMetric import StructuralMetric
from m4i_metrics.physical.PhysicalMetric import PhysicalMetric
from m4i_metrics.textual.TextualMetric import TextualMetric

report_categories = [TextualMetric, StructuralMetric, ProcessMetric, PhysicalMetric]

chart_plot_width = 800
chart_plot_height = 400

model_options = {
    'projectName': 'test project 3093209',
    'projectOwner': 'thijsfranck',
    'branchName': 'MASTER',
    'version': 1578636045410,
    'userid': 'thijsfranck'
}

auth_options = {
    'username': 'thijsfranck',
    'password': 'aurelius17'
}

model = ArchimateUtils.load_model_from_repository(
    **model_options, **auth_options)


def load_exemptions(metric_name):
    projectid = f"{model_options['projectOwner']}__{model_options['projectName'].replace(' ', '_')}"
    project_metadata = PlatformApi.retrieve_project(projectid, **auth_options)
    project_id = project_metadata.id

    branches = PlatformApi.get_branches(project_id, **auth_options)
    branch_with_name = next(
        (branch for branch in branches if branch.name == model_options['branchName']), None)

    exemptions = PlatformApi.get_metric_exemptions(
        project_id,
        branch_id=branch_with_name.id,
        metric_name=metric_name,
        version=model_options['version'],
        **auth_options
    )

    return exemptions
# END load_exemptions


def get_metric_data(metric: Metric):
    metric_results = metric.calculate(model)

    exemptions = load_exemptions(metric.label)

    return metric_results, exemptions
# END


def get_category_data(metric_category: MetricCategory):

    results_per_metric = []
    exemptions_per_metric = []

    for metric in metric_category.metrics:

        metric_results, exemptions = get_metric_data(metric)

        results_per_metric.append(metric_results)
        exemptions_per_metric.append(exemptions)
    # END LOOP

    return results_per_metric, exemptions_per_metric
# END get_category_data


def create_metric_report(metric: Metric, metric_results, exemptions):
    metric_layout = []

    dataset_tabs = [
        Panel(child=grid['grid'], title=grid['name'])
        for grid in create_metric_grid(
            metric_result=metric_results,
            exemptions=exemptions
        )
    ]

    metric_layout.append(Tabs(tabs=dataset_tabs))

    return layout(metric_layout, sizing_mode='scale_width')
# END create_metric_report


def create_category_grid(metric_category: MetricCategory, results_per_metric, exemptions_per_metric):

    summary = metric_category.summarize(
        metric_results=results_per_metric,
        exemptions_per_metric=exemptions_per_metric
    )

    category_chart = metric_category.create_graph(
        data=summary['Summary']['data']
    )

    category_chart.plot_width = chart_plot_width
    category_chart.plot_height = chart_plot_height

    category_layout = []
    category_layout.append([category_chart])

    metric_tabs = []

    for index, metric in enumerate(metric_category.metrics):

        metric_report = create_metric_report(
            metric=metric,
            metric_results=results_per_metric[index],
            exemptions=exemptions_per_metric[index]
        )

        metric_tabs.append(
            Panel(
                child=metric_report,
                title=metric.label
            )
        )
    # END LOOP

    category_layout.append(Tabs(tabs=metric_tabs))
    grid = layout(category_layout, sizing_mode='scale_width')

    return {'name': metric_category.metric_label.capitalize(), 'grid': grid}
# END create_category_grid


def create_report():

    report_layout = []

    report_tabs = []

    for category in report_categories:
        results_per_metric, exemptions_per_metric = get_category_data(
            metric_category=category
        )

        category_grid = create_category_grid(
            metric_category=category,
            results_per_metric=results_per_metric,
            exemptions_per_metric=exemptions_per_metric
        )

        report_tabs.append(
            Panel(
                child=category_grid['grid'],
                title=category_grid['name']
            )
        )
    # END LOOP

    report_layout.append(Tabs(tabs=report_tabs))

    return layout(report_layout, sizing_mode='scale_width')
# END create_report


output_file("test.html")
show(create_report())
