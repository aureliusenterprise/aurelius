import math
from abc import ABC
from typing import Any, Dict, List, Optional

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from m4i_metrics.MetricColumnConfig import MetricColumnConfig
from m4i_metrics.MetricConfig import MetricConfig

from .utils.filter_exempted_concepts import filter_exempted_concepts


def _get_id_column(config: Any) -> Optional[str]:
    if isinstance(config, MetricConfig):
        return config.id_column
    else:
        return config["id_column"]
    # END IF


# END _get_id_column


class MetricCategory(ABC):
    metric_label: str = "metric_category"
    """
    The metric label is used to refer to this category.
    Inheriting classes should override with a unique label of their own.
    """

    metrics: List[Any] = []
    """
    Define which metrics belong to this category in this variable.
    You can add a metric by adding a reference to its class here.
    Inheriting classes should override.
    """

    config = MetricConfig(
        description="This is a summary of the metrics which belong to this category",
        id_column=None,
        data={
            "metric": MetricColumnConfig(
                displayName="Metric", description="The name of the aggregated metric"
            ),
            "compliant": MetricColumnConfig(
                displayName="# of compliant elements",
                description="The total amount of elements compliant with this metric",
            ),
            "non compliant": MetricColumnConfig(
                displayName="# of non-compliant elements",
                description="The total amount of elements non-compliant with this metric",
            ),
            "exempted": MetricColumnConfig(
                displayName="# of exempt elements",
                description="The total amount of elements exempt from this metric",
            ),
        },
    )
    """
    This is the default config for a metric category. Inheriting classes can override.
    """

    @classmethod
    def summarize(
        cls, metric_results: Any = None, exemptions_per_metric: Any = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Creates a summary of the results for every metric in this category.

        As arguments, you should pass:

            * The previously calculated results of every metric that belongs to this category as a list
            * The exemptions for every metric that belongs to this category as a list of lists

        **Both lists should be in the same order as the metrics in this category!**

        :return: A summary of this metric category
        :rtype: Dict[str, Dict[str, Any]]
        """
        if metric_results is None:
            metric_results = []
        if exemptions_per_metric is None:
            exemptions_per_metric = []
        summary_per_metric: List[Dict[str, Any]] = []

        # Iterate over the metrics that belong to this category to create the summary
        for index, metric in enumerate(cls.metrics):
            # Retrieve the exemptions and the metric results at the index of the metric.
            # If there are none given, use empty values as defaults
            exemptions: List[Any] = exemptions_per_metric[index] if index < len(exemptions_per_metric) else []

            metric_result: Dict[str, Any] = metric_results[index] if index < len(metric_results) else {}

            # Create a list of exempted concept ids
            exempted_ids: List[str] = [exemption.concept_id for exemption in exemptions]

            # Iterate over every dataset of the metric result and aggregate the total number of compliant,
            # exempted and non-compliant concepts
            total_compliant: int = 0
            total_exempted: int = 0
            total_non_compliant: int = 0

            for dataset in metric_result.values():
                non_exempted, exempted = filter_exempted_concepts(
                    violations=dataset["data"],
                    id_column=_get_id_column(dataset["config"]) or "",
                    exempted_ids=exempted_ids,
                )
                total_compliant += dataset["sample_size"] - (len(non_exempted.index) + len(exempted.index))
                total_exempted += len(exempted.index)
                total_non_compliant += len(non_exempted.index)
            # END LOOP

            # Append the summary of this metric to the total summary
            summary_per_metric.append(
                {
                    "metric": metric.label,
                    "compliant": total_compliant,
                    "non compliant": total_non_compliant,
                    "exempted": total_exempted,
                }
            )
        # END LOOP

        return {
            "Summary": {"config": cls.config, "data": pd.DataFrame(summary_per_metric), "type": "aggregate"}
        }

    # END summarize

    @staticmethod
    def create_graph(data: pd.DataFrame) -> Any:
        """
        Creates a chart based on the summary data for this category.

        :param data: Summary data for this category
        :type data: pd.DataFrame
        :return: A chart representing the given summary data
        :rtype: bokeh.plotting.Figure
        """
        data_: ColumnDataSource = ColumnDataSource(data)  # type: ignore[reportGeneralTypeIssues]

        p: Any = figure(
            x_range=data["metric"].to_list(),  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
            title="Distribution of compliance per concept type",
            toolbar_location=None,
            tools="",
        )

        legend: Dict[str, str] = {"compliant": "#228B22", "exempted": "#718dbf", "non compliant": "#e84d60"}

        p.vbar_stack(
            stackers=list(legend.keys()),
            x="metric",
            width=0.9,
            color=list(legend.values()),
            source=data_,
            legend=[f"{category} " for category in legend.keys()],
        )

        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.legend.location = "top_left"
        p.xaxis.major_label_orientation = math.pi / 4

        return p

    # END of create_graph


# END MetricCategory
