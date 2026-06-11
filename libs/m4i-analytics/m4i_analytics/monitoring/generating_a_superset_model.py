import json
from datetime import datetime

from pandas import DataFrame
from sqlalchemy import MetaData, Table, create_engine, select

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import ArchimateModel, ViewAttribute
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute
from m4i_analytics.graphs.visualisations.GraphPlotter import Layout
from m4i_analytics.m4i.portal.model.superset.slices.SliceFactory import SliceFactory


def getConnection(db):
    engine = create_engine(db, echo=False)
    return engine


# END getConnection


def getTableData(con, metadata, tablename):
    table = Table(tablename, metadata, autoload=True, autoload_with=con)
    return con.execute(select([table])).fetchall()


# END getTableData


def formatTableName(db_name, schema_name, table_name):
    return "{}.{}{}".format(db_name, (f"{schema_name}.") * bool(schema_name), table_name)


# END formatTableName


def getDBName(url):
    return url.split("/")[-1]


# END getDBName


def generate_superset_model(db_url):
    script_name = "superset model generator"

    con = getConnection(db_url)
    metadata = MetaData()
    metadata.reflect(bind=con, views=True)

    # Content Tables
    slices = getTableData(con, metadata, "slices")
    slice_types = list(set([slice[8] for slice in slices]))
    dashboards = getTableData(con, metadata, "dashboards")
    tables = getTableData(con, metadata, "tables")
    metrics = getTableData(con, metadata, "sql_metrics")
    users = getTableData(con, metadata, "ab_user")
    table_columns = getTableData(con, metadata, "table_columns")
    databases = getTableData(con, metadata, "dbs")

    # Mapping Tables
    dashboard_slices = getTableData(con, metadata, "dashboard_slices")
    dashboard_users = getTableData(con, metadata, "dashboard_user")
    slice_users = getTableData(con, metadata, "slice_user")

    def getSliceColumns(slice_id):
        result = []

        matching_slices = [slice for slice in slices if slice[2] == slice_id]

        if len(matching_slices) > 0:
            params = dict(matching_slices[0])
            params["db_con"] = con
            params["db_metadata"] = metadata

            slice = SliceFactory().create(matching_slices[0][8], **params)

            if slice is not None:
                result = slice.directColumnDependencies()

        return result

    # END getUsedColumns

    def getTableName(table_id):
        result = ""
        if table_id is not None:
            table = [table for table in tables if table[2] == table_id][0]
            result = formatTableName(
                getDBName([db[4] for db in databases if db[2] == table[6]][0]), table[14], table[3]
            )
        return result

    # END getTableName

    def getDashboardFilteredValuesPerColumn(dashboard_id):
        dashboard = next(d for d in dashboards if d[2] == dashboard_id)

        metadata = dashboard[10]

        result = {}
        if metadata:
            json_metadata = json.loads(metadata)
            if json_metadata.get("default_filters"):
                filter_settings = json.loads(json_metadata["default_filters"])

                for slice_id in filter_settings:
                    column_name_mapping = {}

                    for column_id in getSliceColumns(slice_id):
                        column = next(col for col in table_columns if col[2] == column_id)
                        column_name_mapping[column[4]] = column_id
                    # END LOOP

                    filter_columns = filter_settings[slice_id].keys()
                    for column_name in filter_columns:
                        value = filter_settings[slice_id][column_name]
                        if not isinstance(value, list):
                            value = [value]
                        results = result.get(column_name_mapping.get(column_name))
                        if results:
                            results.extend(value)
                        else:
                            result[column_name_mapping.get(column_name)] = value
                    # END LOOP
                # END LOOP
        return result

    # END getDashboardFilteredValuesPerColumn

    # Add the nodes to the model first
    abstract_nodes = [
        {"id": "slicetype", "name": "visualization type", "type": ElementType.BUSINESS_INTERFACE},
        {"id": "dashboard", "name": "dashboard", "type": ElementType.BUSINESS_INTERFACE},
        {"id": "table", "name": "table", "type": ElementType.DATA_OBJECT},
        {"id": "metric", "name": "metric", "type": ElementType.DATA_OBJECT},
        {"id": "user", "name": "user", "type": ElementType.BUSINESS_ACTOR},
        {"id": "column", "name": "column", "type": ElementType.DATA_OBJECT},
    ]

    dashboard_nodes = [
        {"id": f"dashboard-{dashboard[2]}", "name": dashboard[3], "type": ElementType.BUSINESS_INTERFACE}
        for dashboard in dashboards
    ]

    slice_nodes = [
        {"id": f"slice-{slice[2]}", "name": slice[3], "type": ElementType.BUSINESS_INTERFACE}
        for slice in slices
    ]

    table_nodes = [
        {"id": getTableName(table[2]), "name": getTableName(table[2]), "type": ElementType.DATA_OBJECT}
        for table in tables
    ]

    def fmt_user(a, b, c):
        return {"id": f"user-{a}", "name": f"{b} {c}", "type": ElementType.BUSINESS_ACTOR}

    # END fmt_user

    nodes = abstract_nodes
    nodes += dashboard_nodes
    nodes += slice_nodes
    nodes += table_nodes
    nodes += [
        {"id": f"slicetype-{index}", "name": slicetype, "type": ElementType.BUSINESS_INTERFACE}
        for index, slicetype in enumerate(slice_types)
    ]
    nodes += [
        {"id": f"column-{column[2]}", "name": column[4], "type": ElementType.DATA_OBJECT}
        for column in table_columns
    ]
    nodes += [
        {"id": f"metric-{metric[2]}", "name": metric[3], "type": ElementType.DATA_OBJECT}
        for metric in metrics
    ]
    nodes += [fmt_user(user[0], user[1], user[2]) for user in users]

    edges = (
        [
            {
                "id": f"dashboardslice-{dashboard_slice[0]}",
                "type": RelationshipType.AGGREGATION,
                "source": f"dashboard-{dashboard_slice[1]}",
                "target": f"slice-{dashboard_slice[2]}",
                "name": "",
            }
            for dashboard_slice in dashboard_slices
        ]
        + [
            {
                "id": f"typeofslice-{slice[2]}",
                "type": RelationshipType.SPECIALIZATION,
                "source": f"slice-{slice[2]}",
                "target": f"slicetype-{slice_types.index(slice[8])}",
                "name": "",
            }
            for slice in slices
        ]
        + [
            {
                "id": f"dashboarduser-{dashboard_user[0]}",
                "type": RelationshipType.ASSIGNMENT,
                "source": f"dashboard-{dashboard_user[1]}",
                "target": f"user-{dashboard_user[2]}",
                "name": "",
            }
            for dashboard_user in dashboard_users
        ]
        + [
            {
                "id": f"sliceuser-{slice_user[0]}",
                "type": RelationshipType.ASSIGNMENT,
                "source": f"user-{slice_user[1]}",
                "target": f"slice-{slice_user[2]}",
                "name": "",
            }
            for slice_user in slice_users
        ]
        + [
            {
                "id": f"tableslice-{slice[2]}",
                "type": RelationshipType.ACCESS,
                "source": f"slice-{slice[2]}",
                "target": getTableName(slice[13]),
                "name": "",
            }
            for slice in slices
        ]
        + [
            {
                "id": f"tablemetric-{metric[2]}",
                "type": RelationshipType.AGGREGATION,
                "source": getTableName(metric[6]),
                "target": f"metric-{metric[2]}",
                "name": "",
            }
            for metric in metrics
        ]
        + [
            {
                "id": f"tablecolumn-{column[2]}",
                "type": RelationshipType.COMPOSITION,
                "source": getTableName(column[3]),
                "target": f"column-{column[2]}",
                "name": "",
            }
            for column in table_columns
        ]
        + [
            {
                "id": f"slicecolumn-{slice[2]}-{column}",
                "type": RelationshipType.ACCESS,
                "source": f"slice-{slice[2]}",
                "target": f"column-{column}",
                "name": "",
            }
            for slice in slices
            for column in getSliceColumns(slice[2])
        ]
        + [
            {
                "id": f"abstractslicetype-{index}",
                "type": RelationshipType.SPECIALIZATION,
                "source": f"slicetype-{index}",
                "target": "slicetype",
                "name": "",
            }
            for index, slicetype in enumerate(slice_types)
        ]
        + [
            {
                "id": f"abstractdashboard-{dashboard[2]}",
                "type": RelationshipType.SPECIALIZATION,
                "source": f"dashboard-{dashboard[2]}",
                "target": "dashboard",
                "name": "",
            }
            for dashboard in dashboards
        ]
        + [
            {
                "id": f"abstracttable-{table[2]}",
                "type": RelationshipType.SPECIALIZATION,
                "source": getTableName(table[2]),
                "target": "table",
                "name": "",
            }
            for table in tables
        ]
        + [
            {
                "id": f"abstractmetric-{metric[2]}",
                "type": RelationshipType.SPECIALIZATION,
                "source": f"metric-{metric[2]}",
                "target": "metric",
                "name": "",
            }
            for metric in metrics
        ]
        + [
            {
                "id": f"abstractuser-{user[0]}",
                "type": RelationshipType.SPECIALIZATION,
                "source": f"user-{user[0]}",
                "target": "user",
                "name": "",
            }
            for user in users
        ]
        + [
            {
                "id": f"abstractcolumn-{column[2]}",
                "type": RelationshipType.SPECIALIZATION,
                "source": f"column-{column[2]}",
                "target": "column",
                "name": "",
            }
            for column in table_columns
        ]
    )
    # + [{'id':'databasetable-%s' % table[2], 'type': RelationshipType.ASSOCIATION,
    #    'source': getTableName(table[2]),
    #    'target': formatTableName(
    #        getDBName(next(db for db in databases if db[2] == table[6])[4]),
    #        table[14], table[3]
    #    ), 'name': ''} for table in tables])
    # + [{'id':'databasecolumn-%s' % column[2], 'type': RelationshipType.ASSOCIATION,
    #    'source': 'column-%s' % column[2],
    #    'target': formatTableName(
    #        getDBName(next(db for db in databases
    #            if db[2] == next(table for table in tables
    #                if table[2] == column[3])[6])[4]),
    #        next(table for table in tables if table[2] == column[3])[14],
    #        next(table for table in tables if table[2] == column[3])[3]
    #    ) + '.' + column[4], 'name': ''} for column in table_columns])

    for dashboard in dashboards:
        filteredColumnValues = getDashboardFilteredValuesPerColumn(dashboard[2])
        for column_id in filteredColumnValues:
            filtervalues = [
                {
                    "id": f"filtervalue-{dashboard[2]}-{column_id}-{value}",
                    "name": value,
                    "type": ElementType.BUSINESS_OBJECT,
                }
                for value in filteredColumnValues[column_id]
            ]
            dashboardfiltervalues = [
                {
                    "id": "dashboardfiltervalue-{}".format(filtervalue["id"]),
                    "type": RelationshipType.ACCESS,
                    "source": f"dashboard-{dashboard[2]}",
                    "target": filtervalue["id"],
                    "name": "",
                }
                for filtervalue in filtervalues
            ]
            nodes.extend(filtervalues)
            edges.extend(dashboardfiltervalues)

            if column_id:
                columnfiltervalues = [
                    {
                        "id": "columnfiltervalue-{}".format(filtervalue["id"]),
                        "type": RelationshipType.ASSOCIATION,
                        "source": f"column-{column_id}",
                        "target": filtervalue["id"],
                        "name": "",
                    }
                    for filtervalue in filtervalues
                ]
                edges.extend(columnfiltervalues)
        # END LOOP
    # END LOOP

    # Add the generated rows to dataframes
    elems = DataFrame(nodes, columns=["id", "name", "type", "label"])
    rels = DataFrame(edges, columns=["id", "name", "type", "label", "source", "target"])

    # Initialize the model
    model = ArchimateModel("generated superset model", elems, rels, defaultAttributeMapping=True)
    name_mapping = model.getNodeAttributeMapping(NodeAttribute.NAME)
    edge_name_mapping = model.getEdgeAttributeMapping(EdgeAttribute.NAME)
    if name_mapping is not None:
        model.putNodeAttributeMapping(NodeAttribute.LABEL, name_mapping)
    if edge_name_mapping is not None:
        model.putEdgeAttributeMapping(EdgeAttribute.LABEL, edge_name_mapping)

    model.organize()

    # The generate view function automatically adds the view to the model and organization
    views = [
        ArchimateUtils.generate_view(
            model,
            name=dashboard["name"],
            layout=Layout.HIERARCHICAL,
            nodes=list(
                set(
                    [
                        node
                        for edge in model.edges.to_dict(orient="records")
                        if edge["source"] == dashboard["id"] or edge["target"] == dashboard["id"]
                        for node in [edge["source"], edge["target"]]
                    ]
                )
            ),
            path=["Views", "Generated superset dashboards"],
        )
        for dashboard in dashboard_nodes
    ]

    views.extend(
        [
            ArchimateUtils.generate_view(
                model,
                name=slice_node["name"],
                layout=Layout.HIERARCHICAL,
                nodes=list(
                    set(
                        ["dashboard"]
                        + [
                            node
                            for edge in model.edges.to_dict(orient="records")
                            if edge["source"] == slice_node["id"] or edge["target"] == slice_node["id"]
                            for node in [edge["source"], edge["target"]]
                        ]
                    )
                ),
                path=["Views", "Generated superset slices"],
            )
            for slice_node in slice_nodes
        ]
    )

    views.extend(
        [
            ArchimateUtils.generate_view(
                model,
                name=table["name"],
                layout=Layout.HIERARCHICAL,
                nodes=list(
                    set(
                        [
                            node
                            for edge in model.edges.to_dict(orient="records")
                            if edge["source"] == table["id"] or edge["target"] == table["id"]
                            for node in [edge["source"], edge["target"]]
                        ]
                    )
                ),
                path=["Views", "Generated superset tables"],
            )
            for table in table_nodes
        ]
    )

    concept_metadata = [
        {
            "id": concept["id"],
            "data": {
                "original_id": concept["id"],
                "created_on": (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0,
                "created_by": script_name,
            },
        }
        for concept in (nodes + edges)
    ]

    view_metadata = [
        {
            "id": view[model.getViewAttributeMapping(ViewAttribute.ID)],
            "data": {
                "original_id": view[model.getViewAttributeMapping(ViewAttribute.ID)],
                "created_on": (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0,
                "created_by": script_name,
            },
        }
        for view in views
    ]

    return {"model": model, "data": concept_metadata + view_metadata}


# END generate_superset_model
