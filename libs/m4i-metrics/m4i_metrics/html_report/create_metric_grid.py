from typing import Any, Dict, List, Sequence

import pandas as pd
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, Div, TableColumn

from m4i_analytics.m4i.platform.model.MetricExemption import MetricExemption

from ..MetricConfig import MetricConfig
from ..utils.filter_exempted_concepts import filter_exempted_concepts


def create_metric_grid(
    metric_result: Dict[str, Dict[str, Any]] = {}, exemptions: Sequence[MetricExemption] = []
) -> List[Dict[str, Any]]:
    grids: List[Dict[str, Any]] = []

    exempted_ids: List[str] = [exemption.concept_id for exemption in exemptions]  # type: ignore[reportGeneralTypeIssues]

    for dataset_name, dataset in metric_result.items():
        heading = widgetbox(Div(text=f"""<p>{dataset["config"].description}</p>"""))  # type: ignore[reportGeneralTypeIssues]

        non_exempted, exempted = filter_exempted_concepts(
            violations=dataset["data"], id_column=dataset["config"].id_column, exempted_ids=exempted_ids
        )

        exempted_grid = _create_partial_grid(
            config=dataset["config"],
            data=exempted,
            text=f"""<p>The model contains {len(exempted.index)} accepted {dataset_name}.</p>""",
            empty_text=f"""<p>The model does not contains any accepted {dataset_name}.</p>""",
        )

        non_exempted_grid = _create_partial_grid(
            config=dataset["config"],
            data=non_exempted,
            text=f"""<p>The model contains {len(non_exempted.index)} non compliant {dataset_name}.</p>""",
            empty_text=f"""<p>The model does not contains any non compliant {dataset_name}.</p>""",
        )

        grid = layout(
            children=[heading, non_exempted_grid, exempted_grid],  # type: ignore[reportGeneralTypeIssues]
            sizing_mode="scale_width",
        )

        grids.append({"name": dataset_name.capitalize(), "grid": grid})
    # END LOOP

    return grids


# END of create_graph


def _create_partial_grid(
    config: MetricConfig, data: pd.DataFrame, text: str, empty_text: str
) -> List[List[Any]]:
    playout_nested: List[List[Any]] = []
    if len(data) > 0:
        div5 = Div(text=text, width=600, height=30)
        playout_nested.append([widgetbox(div5)])  # type: ignore[reportGeneralTypeIssues]
        columns: List[str] = []
        columns2: List[TableColumn] = []

        for key, value in config.data.items():  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
            columns.append(key)
            columns2.append(TableColumn(field=key, title=value.displayName))  # type: ignore[reportGeneralTypeIssues]
        # END LOOP

        source2 = ColumnDataSource(data[columns])

        data_table2 = DataTable(source=source2, columns=columns2, width=800, height=280, editable=True)
        playout_nested.append([widgetbox(data_table2)])  # type: ignore[reportGeneralTypeIssues]
    else:
        div5 = Div(text=empty_text, width=600, height=30)
        playout_nested.append([widgetbox(div5)])  # type: ignore[reportGeneralTypeIssues]
    # END IF
    return playout_nested


# END of _create_parial_graph
