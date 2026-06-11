import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

import sqlparse

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import ArchimateModel, ViewAttribute
from m4i_analytics.graphs.visualisations.GraphPlotter import Layout


def generate_nifi_model(xml_paths):
    script_name = "nifi model generator"

    dbcp_type_name = "org.apache.nifi.dbcp.DBCPConnectionPool"
    db_url_prop_name = "Database Connection URL"
    db_controller_id_prop = "Database Connection Pooling Service"

    http_context_prop_name = "HTTP Context Map"

    model = ArchimateModel("nifi_model", defaultAttributeMapping=True)

    views = []

    element_metadata = []

    process_views = []
    data_views = []

    for path in xml_paths:
        with gzip.open(path, "r") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            rootGroup = root.find("rootGroup")

            def parse_process_group(rootnode, path=None):
                if path is None:
                    path = []
                print("1")
                process_group_id = rootnode.find("id").text
                process_group = rootnode.find("name").text

                path = list(path)
                path.append(process_group)

                # parse children
                process_groups = rootnode.findall("processGroup")
                for child in process_groups + rootnode.findall("template"):
                    parse_process_group(child, path)
                # END LOOP

                # if this is a template, continue on with the snippet instead
                if rootnode.find("snippet"):
                    rootnode = rootnode.find("snippet")

                processors = rootnode.findall("processors") + rootnode.findall("processor")
                connections = rootnode.findall("connections") + rootnode.findall("connection")
                controller_services = rootnode.findall("controllerServices") + rootnode.findall(
                    "controllerService"
                )
                labels = rootnode.findall("labels") + rootnode.findall("label")

                def formatTableName(db_name, schema_name, table_name):
                    return "{}.{}{}".format(db_name, (f"{schema_name}.") * bool(schema_name), table_name)

                # END formatTableName

                def getColumnNames(token):
                    if isinstance(token, sqlparse.sql.Function):
                        return getColumnNames(token.get_parameters())

                    if isinstance(token, sqlparse.sql.Identifier):
                        # Sometimes a function is still hidden inside an identifier
                        # (e.g. if the function result has an alias)
                        if isinstance(token[0], sqlparse.sql.Function):
                            return getColumnNames(token[0].get_parameters())

                        return [token.get_real_name()]

                    elif isinstance(token, sqlparse.sql.TokenList):
                        return [column for subset in token.tokens for column in getColumnNames(subset)]

                    else:
                        return []

                # END getColumnNames

                print("2")

                def find_x(processor):
                    result = 0
                    position = processor.find("position")
                    if position.find("x") is not None:
                        result = position.find("x").text
                    elif position.attrib.get("x"):
                        result = position.attrib["x"]
                    return result

                # END find_x

                def find_y(processor):
                    result = 0
                    position = processor.find("position")
                    if position.find("y") is not None:
                        result = position.find("y").text
                    elif position.attrib.get("y"):
                        result = position.attrib["y"]
                    return result

                # END find_y

                process_group_nodes = [
                    {
                        "id": "processgroup-{}".format(p.find("id").text),
                        "name": p.find("name").text,
                        "label": p.find("name").text,
                        "type": ElementType.APPLICATION_PROCESS,
                        "x": find_x(p),
                        "y": find_y(p),
                    }
                    for p in process_groups
                ]
                print("3")
                controller_services = [
                    {
                        "id": "controllerservice-{}".format(cs.find("id").text),
                        "name": cs.find("name").text,
                        "label": cs.find("name").text,
                        "type": ElementType.APPLICATION_COMPONENT,
                        "db_name": next(
                            (
                                prop.find("value").text.split("/")[-1]
                                for prop in (cs.find("properties").findall("entry") + cs.findall("property"))
                                if (prop.find("key") and prop.find("key").text == db_url_prop_name)
                                or (prop.find("name") and prop.find("name").text == db_url_prop_name)
                            ),
                            None,
                        )
                        if (cs.find("type") and cs.find("type").text == dbcp_type_name)
                        or (cs.find("class") and cs.find("class").text == dbcp_type_name)
                        else None,
                    }
                    for cs in controller_services
                ]

                def get_processor_properties(processor):
                    if processor.find("config"):
                        return processor.find("config").find("properties").findall("entry")
                    return processor.findall("property")

                # END get_procesor_properties

                def find_property_name(prop):
                    if prop.find("key") is not None:
                        return prop.find("key").text
                    return prop.find("name").text

                # END find_property_name

                def fmt_table(statement):
                    try:
                        result = statement.tokens[8].get_real_name()
                    except Exception:
                        try:
                            result = statement.tokens[6].get_real_name()
                        except Exception:
                            result = None
                    return result

                # END fmt_table
                print("4")
                processor_nodes = [
                    {
                        "id": "processor-{}".format(processor.find("id").text),
                        "name": processor.find("name").text,
                        "label": processor.find("name").text,
                        "type": ElementType.APPLICATION_PROCESS,
                        "db_connection": next(
                            (
                                prop.find("value").text
                                for prop in get_processor_properties(processor)
                                if find_property_name(prop) == db_controller_id_prop
                                and prop.find("value") is not None
                            ),
                            None,
                        ),
                        "http_context": next(
                            (
                                prop.find("value").text
                                for prop in get_processor_properties(processor)
                                if find_property_name(prop) == http_context_prop_name
                                and prop.find("value") is not None
                            ),
                            None,
                        ),
                        "columns": [
                            str(column)
                            for prop in get_processor_properties(processor)
                            if prop.find("value") is not None and "sql" in find_property_name(prop).lower()
                            for statement in sqlparse.parse(prop.find("value").text)
                            for query in statement
                            for column in getColumnNames(query)
                        ],
                        "table": formatTableName(
                            next(
                                (
                                    cs["db_name"]
                                    for cs in controller_services
                                    if cs["id"]
                                    == "controllerservice-{}".format(
                                        next(
                                            (
                                                prop.find("value").text
                                                for prop in get_processor_properties(processor)
                                                if find_property_name(prop) == db_controller_id_prop
                                                and prop.find("value") is not None
                                            ),
                                            None,
                                        )
                                    )
                                ),
                                None,
                            ),
                            None,
                            next(
                                (
                                    fmt_table(statement)
                                    for prop in get_processor_properties(processor)
                                    if prop.find("value") is not None
                                    and "sql" in find_property_name(prop).lower()
                                    for statement in sqlparse.parse(prop.find("value").text)
                                ),
                                None,
                            ),
                        ),
                        "x": float(find_x(processor)),
                        "y": float(find_y(processor)),
                    }
                    for processor in processors
                ]
                print("5")
                tables = [
                    {
                        "id": processor_node["table"],
                        "name": processor_node["table"],
                        "label": processor_node["table"],
                        "type": ElementType.DATA_OBJECT,
                    }
                    for processor_node in processor_nodes
                    if processor_node["table"] != "None.None"
                ]
                print("6")
                columns = [
                    {
                        "id": "{}.{}".format(processor_node["table"], column),
                        "name": "{}.{}".format(processor_node["table"], column),
                        "label": "{}.{}".format(processor_node["table"], column),
                        "type": ElementType.DATA_OBJECT,
                    }
                    for processor_node in processor_nodes
                    for column in processor_node["columns"]
                ]

                nodes = process_group_nodes + controller_services + processor_nodes + tables + columns

                processor_controller_db = [
                    {
                        "id": "realization-{}-{}".format(processor["db_connection"], processor["id"]),
                        "name": processor["name"],
                        "label": processor["name"],
                        "source": "controllerservice-{}".format(processor["db_connection"]),
                        "target": processor["id"],
                        "type": RelationshipType.REALIZATION,
                    }
                    for processor in processor_nodes
                    if processor.get("db_connection") is not None
                ]

                processor_controller_http = [
                    {
                        "id": "realization-{}-{}".format(processor["http_context"], processor["id"]),
                        "name": processor["name"],
                        "label": processor["name"],
                        "source": "controllerservice-{}".format(processor["http_context"]),
                        "target": processor["id"],
                        "type": RelationshipType.REALIZATION,
                    }
                    for processor in processor_nodes
                    if processor.get("http_context") is not None
                ]

                processor_controller = processor_controller_db + processor_controller_http

                processor_group = [
                    {
                        "id": "aggregation-{}-{}".format(process_group_id, processor["id"]),
                        "name": "",
                        "label": "",
                        "source": f"processgroup-{process_group_id}",
                        "target": processor["id"],
                        "type": RelationshipType.AGGREGATION,
                    }
                    for processor in processor_nodes
                ]

                process_group_hierarchy = [
                    {
                        "id": "specialization-{}-{}".format(process_group_id, pg["id"]),
                        "name": "",
                        "label": "",
                        "source": f"processgroup-{process_group_id}",
                        "target": pg["id"],
                        "type": RelationshipType.AGGREGATION,
                    }
                    for pg in process_group_nodes
                ]

                table_column = [
                    {
                        "id": "tablecolumn-{}.{}".format(processor["table"], column),
                        "name": "",
                        "label": "",
                        "source": processor["table"],
                        "target": "{}.{}".format(processor["table"], column),
                        "type": RelationshipType.COMPOSITION,
                    }
                    for processor in processor_nodes
                    for column in processor["columns"]
                ]

                processor_column = [
                    {
                        "id": "processorcolumn-{}-{}".format(processor["id"], column),
                        "name": "",
                        "label": "",
                        "source": processor["id"],
                        "target": "{}.{}".format(processor["table"], column),
                        "type": RelationshipType.ACCESS,
                    }
                    for processor in processor_nodes
                    for column in processor["columns"]
                ]

                queues = []
                queue_access = []

                def get_connection_source(connection):
                    if connection.find("source") is not None:
                        result = connection.find("source").find("id").text
                    else:
                        result = connection.find("sourceId").text
                    return result

                # END get_connection_source

                def get_connection_target(connection):
                    if connection.find("destination") is not None:
                        result = connection.find("destination").find("id").text
                    else:
                        result = connection.find("destinationId").text
                    return result

                # END get_connection_target
                print("7")
                for connection in connections:
                    source = [
                        processor
                        for processor in processor_nodes
                        if processor["id"] == f"processor-{get_connection_source(connection)}"
                    ]
                    target = [
                        processor
                        for processor in processor_nodes
                        if processor["id"] == f"processor-{get_connection_target(connection)}"
                    ]

                    if source and target:
                        source = source[0]
                        target = target[0]

                        queue = {
                            "id": "queue-{}-{}".format(source["id"], target["id"]),
                            "name": "Queue",
                            "label": "Queue",
                            "type": ElementType.DATA_OBJECT,
                            "x": (min(source["x"], target["x"]) + max(source["x"], target["x"])) / 2,
                            "y": (min(source["y"], target["y"]) + max(source["y"], target["y"])) / 2,
                        }

                        queues.append(queue)

                        queue_access.extend(
                            [
                                {
                                    "id": "access-{}-{}".format(source["id"], queue["id"]),
                                    "name": "",
                                    "label": "",
                                    "source": source["id"],
                                    "target": queue["id"],
                                    "type": RelationshipType.ACCESS,
                                    "accessType": "Write",
                                },
                                {
                                    "id": "access-{}-{}".format(target["id"], queue["id"]),
                                    "name": "",
                                    "label": "",
                                    "source": target["id"],
                                    "target": queue["id"],
                                    "type": RelationshipType.ACCESS,
                                    "accessType": "Read",
                                },
                            ]
                        )
                # END LOOP

                nodes += queues
                print("8")
                edges = (
                    [
                        {
                            "id": "trigger-{}".format(connection.find("id").text),
                            "name": "",
                            "label": "",
                            "source": f"processor-{get_connection_source(connection)}",
                            "target": f"processor-{get_connection_target(connection)}",
                            "type": RelationshipType.TRIGGERING,
                        }
                        for connection in connections
                    ]
                    + queue_access
                    + processor_controller
                    + table_column
                    + processor_column
                    + processor_group
                    + process_group_hierarchy
                )
                print("9")
                if nodes:
                    model.nodes = model.nodes.append(nodes)
                if edges:
                    model.edges = model.edges.append(edges)

                flow_nodes = processor_nodes + queues + process_group_nodes

                def label_name(label):
                    result = ""
                    if label.find("label") is not None:
                        result = label.find("label").text
                    elif label.find("value") is not None:
                        result = label.find("value").text
                    return result

                # END label_name

                def label_x(label):
                    result = 0
                    position = label.find("position")
                    if position.find("x") is not None:
                        result = position.find("x").text
                    elif position.attrib.get("x") is not None:
                        result = position.attrib.get("x")
                    return result

                # END label_x

                def label_y(label):
                    result = 0
                    position = label.find("position")
                    if position.find("y") is not None:
                        result = position.find("y").text
                    elif position.attrib.get("y") is not None:
                        result = position.attrib.get("y")
                    return result

                # END label_y

                def label_width(label):
                    result = 0
                    if label.find("width") is not None:
                        result = label.find("width").text
                    elif label.find("size") is not None and label.find("size").attrib.get("width"):
                        result = label.find("size").attrib.get("width")
                    return result

                # END label_width

                def label_height(label):
                    result = 0
                    if label.find("height") is not None:
                        result = label.find("height").text
                    elif label.find("size") is not None and label.find("size").attrib.get("height"):
                        result = label.find("size").attrib.get("height")
                    return result

                # END label_height

                view_labels = [
                    {
                        "id": "label-{}".format(label.find("id").text),
                        "name": label_name(label),
                        "x": int(round(float(label_x(label)))),
                        "y": int(round(float(label_y(label)))),
                        "width": int(round(float(label_width(label)))),
                        "height": int(round(float(label_height(label)))),
                    }
                    for label in labels
                ]
                print("10")
                process_views.append(
                    {
                        "rootnode": rootnode,
                        "name": process_group,
                        "view_nodes": flow_nodes,
                        "labels": view_labels,
                        "path": path,
                    }
                )

                for processor in processor_nodes:
                    con = [pc["source"] for pc in processor_controller if pc["target"] == processor["id"]]
                    col = [pc["target"] for pc in processor_column if pc["source"] == processor["id"]]
                    tab = [tc["target"] for tc in table_column if tc["source"] in col]
                    view_nodes = con + col + tab

                    if view_nodes:
                        data_views.append(
                            {"process_group": process_group, "processor": processor, "view_nodes": view_nodes}
                        )

                # END LOOP

                concept_metadata = [
                    {
                        "id": concept["id"],
                        "data": {
                            "original_id": concept["id"],
                            "created_on": (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()
                            * 1000.0,
                            "created_by": script_name,
                        },
                    }
                    for concept in (nodes + edges)
                ]

                element_metadata.extend(concept_metadata)

            # END parse_process_group

            parse_process_group(rootGroup)

        # END WITH
    # END LOOP

    model.organize()

    for process_view in process_views:
        views.append(
            ArchimateUtils.generate_view(
                model,
                name=process_view["name"],
                nodes=[node["id"] for node in process_view["view_nodes"]],
                layout=Layout.MANUAL,
                coords={node["id"]: [node["x"], node["y"]] for node in process_view["view_nodes"]},
                labels=process_view["labels"],
                path=["Views"] + process_view["path"],
            )
        )
    # END LOOP

    for data_view in data_views:
        views.append(
            ArchimateUtils.generate_view(
                model,
                name="{}-{}".format(data_view["process_group"], data_view["processor"]["name"]),
                nodes=data_view["view_nodes"] + [data_view["processor"]["id"]],
                layout=Layout.HIERARCHICAL,
                path=["Views", "Data dependencies"],
            )
        )
    # END LOOP

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

    element_metadata.extend(view_metadata)

    return {"model": model, "data": element_metadata}


# END generate_nifi_model
