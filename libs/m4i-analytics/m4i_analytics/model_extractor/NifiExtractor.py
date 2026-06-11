import re
import xml.etree.ElementTree as ET

import numpy as np

# import sqlparse
import pandas as pd

from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import ArchimateModel
from m4i_analytics.graphs.visualisations.GraphPlotter import Layout
from m4i_analytics.model_extractor.extract_tables import extract_statement_type, extract_tables

# from datetime import datetime
from m4i_analytics.model_extractor.ExtractorLanguagePrimitives import ExtractorLanguagePrimitives

# import numbers


# %%
class NifiExtractor:
    @staticmethod
    def extract_nifi_model(xml_paths, data_only=False):
        # %%
        xml_paths = ["C:/Local/Delphi/pilot/delphi_azure/flow.xml"]
        # xml_paths = ['C:/Local2/code/analytics-library/m4i_analytics/model_extractor/flow.xml']
        print(xml_paths)

        print("start")
        script_name = "nifi model extractor"

        element_metadata = []

        process_group_nodes = []
        processor_nodes = []
        controller_service_nodes = []
        label_nodes = []
        port_nodes = []
        connection_nodes = []

        process_group_df = pd.DataFrame()
        processor_df = pd.DataFrame()
        controller_service_df = pd.DataFrame()
        label_df = pd.DataFrame()
        port_df = pd.DataFrame()
        connection_df = pd.DataFrame()

        for path in xml_paths:
            print("retireve root elements")

            tree = ET.parse(path)
            root = tree.getroot()
            rootGroup = root.find("rootGroup")
            rootnode = rootGroup

            def parse_process_group(rootnode, parent=None, path=None):
                if path is None:
                    path = []
                process_group_nodes = []
                processor_nodes = []
                controller_service_nodes = []
                label_nodes = []
                port_nodes = []
                connection_nodes = []

                print("parsing process group")

                process_group_id = "id-{}".format(rootnode.find("id").text)
                process_group = rootnode.find("name").text

                path = list(path)
                path.append(process_group)

                # parse children
                process_groups = rootnode.findall("processGroup")
                for child in process_groups:
                    res = parse_process_group(child, process_group_id, path)
                    process_group_nodes.extend(res["process_group_nodes"])
                    processor_nodes.extend(res["processor_nodes"])
                    controller_service_nodes.extend(res["controller_service_nodes"])
                    label_nodes.extend(res["label_nodes"])
                    port_nodes.extend(res["port_nodes"])
                    connection_nodes.extend(res["connection_nodes"])
                # END LOOP
                for child in rootnode.findall("template"):
                    res = parse_process_group(child, process_group_id, path + ["template"])
                    process_group_nodes.extend(res["process_group_nodes"])
                    processor_nodes.extend(res["processor_nodes"])
                    controller_service_nodes.extend(res["controller_service_nodes"])
                    label_nodes.extend(res["label_nodes"])
                    port_nodes.extend(res["port_nodes"])
                    connection_nodes.extend(res["connection_nodes"])
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
                ports = (
                    rootnode.findall("inputPort")
                    + rootnode.findall("inputPorts")
                    + rootnode.findall("outputPort")
                    + rootnode.findall("outputPorts")
                )

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

                def find_parentGroupId(processor):
                    result = None
                    # if processor.findtext('parentGroupId') is not None :
                    result = processor.findtext("parentGroupId")
                    # elif position.attrib.get('x'):
                    #    result = position.attrib['x']
                    return result

                # END find_parentGroupId

                print("process group nodes")

                process_group_nodes2 = [
                    {
                        "id": "id-{}".format(process_group.find("id").text),
                        "groupId": f"id-{process_group_id}",
                        "type": "process_group",
                        "name": process_group.find("name").text,
                        "path": path,
                        "parent": parent,
                        "parentGroupId": find_parentGroupId(process_group),
                        "x": find_x(process_group),
                        "y": find_y(process_group),
                    }
                    for process_group in process_groups
                ]
                process_group_nodes.extend(process_group_nodes2)
                print("controller services")

                def find_class(controller_service):
                    result = None
                    if controller_service.find("class") is not None:
                        result = controller_service.find("class").text
                    elif controller_service.find("type") is not None:
                        result = controller_service.find("type").text
                    return result

                # END find_class

                def find_enabled(controller_service):
                    result = None
                    if controller_service.find("enabled") is not None:
                        result = controller_service.find("enabled").text
                    elif controller_service.find("state") is not None:
                        result = controller_service.find("state").text
                    return result

                # END find_enabled

                def find_comment(controller_service):
                    result = None
                    if controller_service.find("comment") is not None:
                        result = controller_service.find("comment").text
                    elif controller_service.find("comments") is not None:
                        result = controller_service.find("comments").text
                    return result

                # END find_enabled

                def add_properties(nn, construct):
                    construct2 = construct
                    if construct.find("config") is not None:
                        construct2 = construct.find("config")
                    for elem in construct2.findall("property"):
                        if elem.find("name") is not None and elem.find("value") is not None:
                            nn["prop_{}".format(elem.find("name").text)] = elem.find("value").text
                    for elem in construct2.findall("properties"):
                        if elem.find("key") is not None and elem.find("value") is not None:
                            nn["prop_{}".format(elem.find("key").text)] = elem.find("value").text
                        if elem.find("entry") is not None:
                            for _elem2 in elem.find("entry"):
                                if elem.find("key") is not None and elem.find("value") is not None:
                                    nn["prop_{}".format(elem.find("key").text)] = elem.find("value").text

                # END OF add_properties

                # controller_service_nodes = []
                if controller_services is not None:
                    for cs in controller_services:
                        # print(cs.find('id').text)
                        nn = {
                            "id": "id-{}".format(cs.find("id").text),
                            "groupId": f"id-{process_group_id}",
                            "type": "controller_service",
                            "name": cs.find("name").text,
                            "path": path,
                            "parent": parent,
                            "parentGroupId": find_parentGroupId(cs),
                            "comment": find_comment(cs),
                            "class": find_class(cs),
                            "enabled": find_enabled(cs),
                        }
                        add_properties(nn, cs)
                        controller_service_nodes.append(nn)
                        # , 'db_name': next((prop.find('value').text.split('/')[-1]
                        #    for prop in (cs.find('properties').findall('entry')
                        #        + cs.findall('property'))
                        #    if (prop.find('key') and prop.find('key').text == db_url_prop_name)
                        #       or (prop.find('name') and prop.find('name').text == db_url_prop_name)),
                        #    None) if (cs.find('type') and cs.find('type').text == dbcp_type_name)
                        #       or (cs.find('class') and cs.find('class').text == dbcp_type_name)
                        #    else None
                        # } for cs in controller_services]

                print("processors")

                # processor_nodes=[]
                for processor in processors:
                    nn = {
                        "id": "id-{}".format(processor.find("id").text),
                        "groupId": f"id-{process_group_id}",
                        "type": "processor",
                        "name": processor.find("name").text,
                        "path": path,
                        "parent": parent,
                        "parentGroupId": find_parentGroupId(processor),
                        "comment": find_comment(processor),
                        "x": float(find_x(processor)),
                        "y": float(find_y(processor)),
                        "class": find_class(processor),
                    }
                    add_properties(nn, processor)
                    processor_nodes.append(nn)

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

                print("labels")

                # label_nodes= []
                for label in labels:
                    nn = {
                        "id": "id-{}".format(label.find("id").text),
                        "groupId": f"id-{process_group_id}",
                        "type": "label",
                        "name": label_name(label),
                        "x": int(round(float(label_x(label)))),
                        "y": int(round(float(label_y(label)))),
                        "width": int(round(float(label_width(label)))),
                        "height": int(round(float(label_height(label)))),
                        "path": path,
                        "parent": parent,
                        "parentGroupId": find_parentGroupId(label),
                    }
                    if label.find("styles") is not None:
                        for style in label.find("styles").findall("style"):
                            if style.attrib["name"] is not None and style.text is not None:
                                nn[style.attrib["name"]] = style.text
                    add_properties(nn, label)
                    label_nodes.append(nn)

                def port_state(port):
                    result = port.findtext("state")
                    if result is None:
                        result = port.findtext("scheduledState")
                    return result

                # END port_state

                def port_name(port):
                    result = ""
                    if port.find("name") is not None:
                        result = port.find("name").text
                    return result

                # END port_name

                print("ports")
                for port in ports:
                    nn = {
                        "id": "id-{}".format(port.find("id").text),
                        "groupId": f"id-{process_group_id}",
                        "type": port.tag,
                        "name": port_name(port),
                        "path": path,
                        "parent": parent,
                        "parentGroupId": find_parentGroupId(port),
                        "comment": find_comment(port),
                        "x": int(round(float(label_x(port)))),
                        "y": int(round(float(label_y(port)))),
                        "port_state": port_state(port),
                    }
                    add_properties(nn, port)
                    port_nodes.append(nn)

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

                print("Queues")

                for con in connections:
                    nn = {
                        "id": "id-{}".format(con.find("id").text),
                        "groupId": f"id-{process_group_id}",
                        "type": con.tag,
                        "name": label_name(con),
                        "path": path,
                        "parent": parent,
                        "parentGroupId": find_parentGroupId(con),
                        "comment": find_comment(con),
                        "source": f"id-{get_connection_source(con)}",
                        "target": f"id-{get_connection_target(con)}",
                        "sourceGroupId": "id-{}".format(con.findtext("sourceGroupId")),
                        "destinationGroupId": "id-{}".format(con.findtext("destinationGroupId")),
                        "relationship": con.findtext("relationship"),
                    }
                    add_properties(nn, con)
                    connection_nodes.append(nn)
                # END LOOP

                return {
                    "process_group_nodes": process_group_nodes,
                    "processor_nodes": processor_nodes,
                    "label_nodes": label_nodes,
                    "controller_service_nodes": controller_service_nodes,
                    "port_nodes": port_nodes,
                    "connection_nodes": connection_nodes,
                }

            # END of method definition
            res = parse_process_group(rootnode)
            process_group_nodes.extend(res["process_group_nodes"])
            processor_nodes.extend(res["processor_nodes"])
            controller_service_nodes.extend(res["controller_service_nodes"])
            label_nodes.extend(res["label_nodes"])
            port_nodes.extend(res["port_nodes"])
            connection_nodes.extend(res["connection_nodes"])

            process_group_df = pd.DataFrame(process_group_nodes)
            processor_df = pd.DataFrame(processor_nodes)
            controller_service_df = pd.DataFrame(controller_service_nodes)
            label_df = pd.DataFrame(label_nodes)
            port_df = pd.DataFrame(port_nodes)
            connection_df = pd.DataFrame(connection_nodes)

        # %%
        # prepare the data
        data_col = [process_group_df, controller_service_df, label_df, port_df, connection_df, processor_df]

        # find URLs
        # data = controller_service_df
        for data in data_col:
            if len(data) > 0:
                data["_url_"] = None
                mask = np.column_stack(
                    [
                        data[col].str.contains(r"http://", case=False, na=False)
                        for col in data.select_dtypes(include=["object"])
                    ]
                )
                mask = np.column_stack(
                    [
                        data[col].str.contains(r"https://", case=False, na=False)
                        for col in data.select_dtypes(include=["object"])
                    ]
                )
                data2 = data.loc[mask.any(axis=1)]
                for index, row in data2.iterrows():
                    for col in data.columns:
                        if (
                            "http://" in str(row[col]).lower()
                            or "https://" in str(row[col]).lower()
                            and "prop_" in col
                        ):
                            data.loc[index, "_url_"] = row[col]
                            print(f"found one: ({index},{col})")

        ii = 0
        for data in data_col:
            if len(data) > 0:
                prop_ports = list(data.columns[data.columns.str.contains(r"port", case=False, na=False)])
                prop_hostnames = list(
                    data.columns[data.columns.str.contains(r"hostname", case=False, na=False)]
                )
                col_list = prop_ports + prop_hostnames
                data["_port_"] = None
                data["_hostname_"] = None

                data3 = pd.DataFrame()
                for col in prop_ports:
                    # col='prop_Listening Port'
                    data3[col] = (
                        data[col]
                        .apply(lambda x: int(x) if str(x).isnumeric() and x == x else None)
                        .rename(col)
                    )
                    # print('%d - %s - %s' % (ii,col,data3.nonzero()))
                data["_port_"] = data3.max(axis=1, skipna=True, numeric_only=True)

                data3 = pd.DataFrame()
                for col in prop_hostnames:
                    # col='prop_snmp-hostname'
                    data3[col] = (
                        data[col]
                        .apply(lambda x: x if x is not None and isinstance(x, str) and len(x) > 8 else "")
                        .rename(col)
                    )
                    # print('%d - %s - %s' % (ii,col,data3.nonzero()))
                data["_hostname_"] = data3.apply(lambda x: "".join(x), axis=1)
                data["_hostname_"] = data.apply(
                    lambda x: "localhost" if x["_hostname_"] == "" and x["_port_"] > 0 else x["_hostname_"],
                    axis=1,
                )
                ii = ii + 1

        # find JDBC connections
        # data = controller_service_df
        for data in data_col:
            if len(data) > 0:
                data["_jdbc_"] = None
                data["_jdbc_protocol_"] = None
                data["_jdbc_host_"] = None
                data["_jdbc_port_"] = None
                data["_jdbc_database_"] = None
                mask = np.column_stack(
                    [
                        data[col].str.contains(r"jdbc:", case=False, na=False)
                        for col in data.select_dtypes(include=["object"])
                    ]
                )
                data2 = data.loc[mask.any(axis=1)]
                for index, row in data2.iterrows():
                    for col in data.columns:
                        if "jdbc:" in str(row[col]):
                            data.loc[index, "_jdbc_"] = row[col]
                            print(f"found one: ({index},{col})")
                            m = re.search("^(.+)//(.*@)?(.+?):(.+?)/(.+?)$", row[col])
                            if m is not None:
                                data.loc[index, "_jdbc_protocol_"] = m.group(1)
                                data.loc[index, "_jdbc_host_"] = m.group(3)
                                data.loc[index, "_jdbc_port_"] = m.group(4)
                                data.loc[index, "_jdbc_database_"] = m.group(5)
                            else:
                                print(f"no proper fomrat {row[col]}")
                                data.loc[index, "_jdbc_protocol_"] = ""
                                data.loc[index, "_jdbc_host_"] = ""
                                data.loc[index, "_jdbc_port_"] = ""
                                data.loc[index, "_jdbc_database_"] = ""

        # find queries connections
        # data = processor_df
        # col = 'prop_SQL select query'
        ii = 0

        for data in data_col:
            if len(data) > 0:
                data["_query_"] = None
                data["_query_type_"] = None
                data["_query_search_string_"] = None
                for searchString in [" from ", "insert ", "update ", "delete "]:
                    mask = np.column_stack(
                        [
                            data[col].str.contains(searchString, case=False, na=False)
                            for col in data.select_dtypes(include=["object"])
                        ]
                    )
                    data2 = data.loc[mask.any(axis=1)]
                    for index, row in data2.iterrows():
                        for col in data.columns:
                            if searchString in str(row[col]).lower():
                                data.loc[index, "_query_"] = row[col]
                                data.loc[index, "_query_search_string_"] = searchString.strip()
                                print(f"found one: ({ii} - {searchString} - {index},{row[col]})")
                # extract table name from query
                data["_table_"] = data["_query_"].apply(lambda x: extract_tables(x))
                data["_query_type_"] = data["_query_"].apply(lambda x: extract_statement_type(x))
                ii = ii + 1

        # find all references in properties
        # data = processor_df
        ids = []
        for data in data_col:
            if len(data) > 0:
                ids.extend(list(data.id.apply(lambda x: x[3:])))
        prop_conn = []
        ii = 0
        for data in data_col:
            if len(data) > 0:
                mask = np.column_stack(
                    [data[col].apply(lambda x: x in ids) for col in data.select_dtypes(include=["object"])]
                )
                data2 = data.loc[mask.any(axis=1)]
                for index, row in data2.iterrows():
                    for col in data.columns:
                        if row[col] in ids:
                            prop_conn.append(
                                {
                                    "id": "{}_{}".format(row["id"], row[col]),
                                    "source": row["id"],
                                    "target": f"id-{row[col]}",
                                    "source_column": col,
                                    "row_reference": index,
                                }
                            )
                            print(f"cross_reference: ({ii} - {index},{col})")
                ii = ii + 1

        prop_conn_df = pd.DataFrame(prop_conn)

        # %%
        # data pre-processing stage 2

        nodes_df = pd.concat([process_group_df, controller_service_df, processor_df])
        nodes_df = nodes_df[
            [
                "id",
                "name",
                "groupId",
                "parent",
                "parentGroupId",
                "path",
                "type",
                "x",
                "y",
                "_url_",
                "_query_",
                "_table_",
                "_query_type_",
                "comment",
                "_jdbc_",
                "_jdbc_protocol_",
                "_jdbc_host_",
                "_jdbc_port_",
                "_jdbc_database_",
                "_port_",
                "_hostname_",
            ]
        ]
        nodes_df = nodes_df.reset_index()

        # processing JDBC URLs
        data_db_agg = pd.DataFrame()
        data_db = nodes_df.loc[nodes_df["_jdbc_"].nonzero()]
        if len(data_db) > 0:
            data_db["key"] = data_db.apply(
                lambda x: (
                    re.sub(r"\W+", "", x["_jdbc_"])
                    if x["_jdbc_host_"] == "" or x["_jdbc_database_"] == ""
                    else "{}_{}".format(x["_jdbc_host_"], x["_jdbc_database_"])
                ),
                axis=1,
            )
            data_db["name"] = data_db.apply(
                lambda x: (
                    x["_jdbc_"]
                    if x["_jdbc_host_"] == "" or x["_jdbc_database_"] == ""
                    else "{} {}".format(x["_jdbc_host_"], x["_jdbc_database_"])
                ),
                axis=1,
            )
            # data['_jdbc_url_san_'] = data['_jdbc_'].apply(lambda x: re.sub(r'\W+', '', x))
            data_db_agg = (
                data_db.groupby(
                    by=[
                        "key",
                        "name",
                        "_jdbc_protocol_",
                        "_jdbc_database_",
                        "_jdbc_",
                        "_jdbc_host_",
                        "_jdbc_port_",
                    ]
                )
                .size()
                .rename("cnt")
                .reset_index()
            )
            data_db_agg["generic_key"] = "generic_database"

        # processing URLs
        data_url = nodes_df.loc[nodes_df["_url_"].nonzero()]
        if len(data_url) > 0:
            data_url["key"] = data_url._url_.apply(lambda x: re.sub(r"\W+", "", x))
            data_url["name"] = data_url._url_

        # processing cip connections
        data_ip = nodes_df.loc[nodes_df["_hostname_"].nonzero()]
        if len(data_ip) > 0:
            data_ip = data_ip[data_ip._port_ > 0]
            data_ip["key"] = data_ip.apply(lambda x: f"{x['_hostname_']}_{int(x['_port_'])}", axis=1)
            data_ip["name"] = data_ip.apply(lambda x: f"{x['_hostname_']}:{int(x['_port_'])}", axis=1)

        # nodes_df['_query_group_']=nodes_df.id.apply(lambda x: [])
        # further prepare data
        data_queries = nodes_df[
            nodes_df.apply(lambda x: x["_query_"] is not None and x["_table_"] != [], axis=1)
        ]
        mapping = list(data_queries.id.apply(lambda x: {"id": x, "group": x}))
        new_ids = list(data_queries["id"])
        completed = []
        while len(new_ids) > 0:
            print(len(new_ids))
            # check first whether there is a database related context attached
            # prop_conn_res = new_ids.merge(prop_conn_df, how = 'inner',
            #    left_on='id', right_on='source')[['id_x','target']]
            prop_conn_res = prop_conn_df[prop_conn_df.source.isin(new_ids)][["source", "target"]]
            nn2 = nodes_df.merge(prop_conn_res, how="inner", right_on="target", left_on="id")
            if len(nn2) > 0:
                for _row in nn2.iterrows():
                    row = _row
                    for elem_ in mapping:
                        if elem_["id"] == row["source"] and elem_["group"] not in completed:
                            rec = {"id": row["target"], "group": elem_["group"]}
                            completed.append(elem_["group"])
                            jdbc_data = data_db.loc[data_db.id == row["target"]]
                            print(jdbc_data)
                            if len(jdbc_data) > 0:
                                # print('miss for key %s' % row['target'])
                                # else:
                                # print('%s.%s' % (jdbc_data['key'], jdbc_data['name']))
                                rec["_jdbc_key_"] = jdbc_data["key"].values[0]
                                rec["_jdbc_name_"] = jdbc_data["name"].values[0]
                                rec["_query_executor_"] = row["source"]
                            mapping.extend([rec])

            # find queries which have not been mapped yet to a service
            remaining_ids = [id_ for id_ in new_ids if id_ not in nn2.source]
            new_ids = []
            mapping_new = []
            if len(remaining_ids) > 0:
                # propagate along the process flow
                rels = nodes_df[nodes_df.id.isin(remaining_ids)].merge(
                    connection_df, how="left", left_on="id", right_on="source"
                )[["id_x", "target"]]
                # determine corresponding nodes
                # I am ignoring relations to ports, since ports can not execute a query.
                # I consider it unlikely that a query is built on one process group
                # and actually executed in a different process group.
                nn3 = nodes_df.merge(rels, how="inner", right_on="target", left_on="id")
                # check whether a node has been visited before for a particular query
                for _row in nn3.iterrows():
                    row = _row
                    src_group = [
                        elem_["group"]
                        for elem_ in mapping
                        if elem_["id"] == row["id_x"] and elem_["group"] not in completed
                    ]
                    trg_group = [
                        elem_["group"]
                        for elem_ in mapping
                        if elem_["id"] == row["target"] and elem_["group"] not in completed
                    ]
                    dif_group = [id_ for id_ in src_group if id_ not in trg_group]
                    if len(dif_group) > 0:
                        mapping_new.extend(
                            [{"id": row["target"], "group": group_id} for group_id in dif_group]
                        )
                        new_ids.append(row["target"])
            mapping.extend(mapping_new)
        # finding the database object the query is related to
        # there are queries which do not have a related jdbc element
        mapping_df = pd.DataFrame(mapping)
        mapping_df = mapping_df.fillna("")
        mapping_agg_jdbc = pd.DataFrame()
        mapping_agg_jdbc_table = pd.DataFrame()
        if len(mapping_df) > 0:
            mapping_agg_jdbc = mapping_df.groupby(by="group").agg({"_jdbc_key_": max, "_jdbc_name_": max})
            mapping_agg_jdbc.columns = ["_jdbc_key_", "_jdbc_name_"]
            mapping_agg_jdbc = mapping_agg_jdbc.reset_index()
            mapping_agg_jdbc = mapping_agg_jdbc[mapping_agg_jdbc._jdbc_key_ != ""]
            mapping_query_table = mapping_df.loc[mapping_df._query_executor_.nonzero()]
            mapping_agg_jdbc[["_query_executor_", "_service_id_"]] = mapping_agg_jdbc.merge(
                mapping_query_table, how="left", on="group"
            )[["_query_executor_", "id"]]
            # mapping_agg_jdbc['_query_executor_'] = mapping_agg_jdbc.merge(
            #    mapping_query_table, how='left', on='group')['_query_executor_']

            # enrich with URL string and some other properties
            query_df = nodes_df[nodes_df.id.isin(mapping_agg_jdbc.group)][
                ["id", "_query_", "_query_type_", "_table_"]
            ]
            query_helper = [
                {"id": row["id"], "_query_": row["_query_"], "_query_type_": qt, "_table_": tt}
                for index, row in query_df.iterrows()
                for qt in row["_query_type_"]
                for tt in row["_table_"]
            ]
            query_df = pd.DataFrame(query_helper)
            query_df = query_df[
                np.logical_and(query_df._query_type_ != "UNKNOWN", query_df._table_ is not None)
            ]

            mapping_agg_jdbc = mapping_agg_jdbc.merge(query_df, how="left", left_on="group", right_on="id")
            mapping_agg_jdbc["name"] = mapping_agg_jdbc.apply(
                lambda x: "{} {}".format(x["_jdbc_name_"], x["_table_"]), axis=1
            )
            mapping_agg_jdbc["key"] = mapping_agg_jdbc.apply(
                lambda x: "{}_{}".format(x["_jdbc_key_"], x["_table_"]), axis=1
            )

            mapping_agg_jdbc_table = (
                mapping_agg_jdbc.groupby(by=["name", "key", "_table_", "_jdbc_key_"])
                .size()
                .rename("cnt")
                .reset_index()
            )
            mapping_agg_jdbc_table["generic_key"] = "generic_table"

            # determine groups a particular concept is related to
            mapping_df["group"] = mapping_df.group.apply(lambda x: [x])
            # there is a chance of loosing some relations to to other databases
            mapping_agg = mapping_df.groupby(by="id").agg(
                {"_jdbc_key_": max, "_jdbc_name_": max, "group": sum}
            )
            mapping_agg.columns = ["_jdbc_key_", "_jdbc_name_", "_query_group_"]
            mapping_agg = mapping_agg.reset_index()
            # nodes_df['_query_group_'] = nodes_df.merge(mapping_agg, how='left', on='id')['_query_group_']

        # %%
        # create model

        nodes_df = pd.concat([process_group_df, processor_df])
        nodes_df = nodes_df[
            [
                "id",
                "name",
                "groupId",
                "parent",
                "parentGroupId",
                "path",
                "type",
                "x",
                "y",
                "_url_",
                "_query_",
                "_table_",
                "_query_type_",
                "comment",
                "_jdbc_",
                "_jdbc_protocol_",
                "_jdbc_host_",
                "_jdbc_port_",
                "_jdbc_database_",
                "class",
            ]
        ]
        nodes_df = nodes_df.reset_index()

        element_metadata = []
        nodes = []
        edges = []
        views = []

        data_only = False
        model = ArchimateModel("nifi_model", defaultAttributeMapping=True)

        # define concepts
        ids = [
            {
                "prefix": "nifi_",
                "id_key": "id",
                "concept_name_prefix": "",
                "concept_name_key": "name",
                "concept_label_prefix": "",
                "concept_label_key": "name",
                "concept_type": ElementType.APPLICATION_PROCESS,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "parent_node", "value": "parent"},
                    {"key": "parentGroupId", "value": "parentGroupId"},
                    {"key": "concept_type", "value": "type"},
                    # ,{'key':'comment', 'value':'comment'}
                    {"key": "id_prefix", "value": "nifi_"},
                    {"key": "nifi_concept_class", "value": "class"},
                    {"key": "nifi_concept_type", "value": "type"},
                    {"key": "path", "value": "path"},
                ],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_concept(nodes_df, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])

        ids = [
            {
                "prefix": "nifi_",
                "id_key": "id",
                "concept_name_prefix": "",
                "concept_name_key": "name",
                "concept_label_prefix": "",
                "concept_label_key": "name",
                "concept_type": ElementType.APPLICATION_EVENT,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "parent_node", "value": "parent"},
                    {"key": "parentGroupId", "value": "parentGroupId"},
                    {"key": "concept_type", "value": "type"},
                    {"key": "port_state", "value": "port_state"},
                    {"key": "id_prefix", "value": "nifi_"},
                    {"key": "nifi_concept_type", "value": "type"},
                    # ,{'key':'comment', 'value':'comment'}
                    {"key": "path", "value": "path"},
                ],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_concept(port_df, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])

        ids = [
            {
                "prefix": "nifi_",
                "id_key": "id",
                "concept_name_prefix": "",
                "concept_name_key": "name",
                "concept_label_prefix": "",
                "concept_label_key": "name",
                "concept_type": ElementType.APPLICATION_SERVICE,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "parent_node", "value": "parent"},
                    {"key": "parentGroupId", "value": "parentGroupId"},
                    {"key": "concept_type", "value": "type"},
                    # ,{'key':'comment', 'value':'comment'}
                    {"key": "id_prefix", "value": "nifi_"},
                    {"key": "nifi_concept_class", "value": "class"},
                    {"key": "nifi_concept_type", "value": "type"},
                    {"key": "path", "value": "path"},
                ],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_concept(controller_service_df, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])

        # add queries related to nodes and the queries they are relating to
        ids = [
            {
                "prefix": "nifi_query_",
                "id_key": "id",
                "concept_name_prefix": "query ",
                "concept_name_key": "_query_",
                "concept_label_prefix": "query ",
                "concept_label_key": "_query_",
                "concept_type": ElementType.DATA_OBJECT,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "query_type", "value": "_query_type_"},
                    {"key": "jdbc_name", "value": "_jdbc_name_"},
                    {"key": "id_prefix", "value": "nifi_query_"},
                ],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_concept(mapping_agg_jdbc, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        nodes.extend(res["nodes"])

        # add table concepts related to nodes and the queries they are relating to
        if "mapping_agg_jdbc_table" in locals() and len(mapping_agg_jdbc_table) > 0:
            ids = [
                {
                    "prefix": "table_",
                    "id_key": "key",
                    "concept_name_prefix": "table ",
                    "concept_name_key": "_table_",
                    "concept_label_prefix": "table ",
                    "concept_label_key": "_query_",
                    "concept_type": ElementType.DATA_OBJECT,
                    "mapping": [
                        {"key": "original_id", "value": "key"},
                        {"key": "table", "value": "_table_"},
                        {"key": "id_prefix", "value": "table_"},
                    ],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_concept(
                mapping_agg_jdbc_table, ids, script_name, data_only
            )
            element_metadata.extend(res["metadata"])
            nodes.extend(res["nodes"])

        ####################################
        # add queues from connections
        # data = connection_df
        # data['key'] = data.apply(lambda x: '%s_%s' %(x['source'],x['target'] ), axis=1)
        ids = [
            {
                "prefix": "nifi_queue_",
                "id_key": "id",
                "concept_name_prefix": "queue ",
                "concept_name_key": "relationship",
                "concept_label_prefix": "queue ",
                "concept_label_key": "relationship",
                "concept_type": ElementType.DATA_OBJECT,
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "parent_node", "value": "parent"},
                    {"key": "parentGroupId", "value": "parentGroupId"},
                    {"key": "concept_type", "value": "type"},
                    {"key": "relationship", "value": "relationship"},
                    # ,{'key':'comment', 'value':'comment'}
                    {"key": "id_prefix", "value": "nifi_queue_"},
                    {"key": "path", "value": "path"},
                ],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_concept(connection_df, ids, script_name, data_only)
        queue_nodes = res["nodes"]
        element_metadata.extend(res["metadata"])
        nodes.extend(queue_nodes)

        # controller service

        ####################################
        # JDBC interfaces
        # nodes
        if "data_db" in locals() and len(data_db) > 0:
            ids = [
                {
                    "prefix": "nifi_jdbc_",
                    "id_key": "id",
                    "concept_name_prefix": "JDBC ",
                    "concept_name_key": "name",
                    "concept_label_prefix": "",
                    "concept_label_key": "name",
                    "concept_type": ElementType.APPLICATION_INTERFACE,
                    "mapping": [
                        {"key": "jdbc_url", "value": "_jdbc_"},
                        {"key": "original_id", "value": "id"},
                        {"key": "jdbc_protocol", "value": "_jdbc_protocol_"},
                        {"key": "jdbc_host_", "value": "_jdbc_host_"},
                        {"key": "jdbc_port_", "value": "_jdbc_port_"},
                        {"key": "jdbc_database_", "value": "_jdbc_database_"},
                        {"key": "id_prefix", "value": "nifi_jdbc_"},
                    ],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_concept(data_db, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            nodes.extend(res["nodes"])

            ids = [
                {
                    "prefix": "database_",
                    "id_key": "key",
                    "concept_name_prefix": "database ",
                    "concept_name_key": "name",
                    "concept_label_prefix": "database ",
                    "concept_label_key": "name",
                    "concept_type": ElementType.DATA_OBJECT,
                    "mapping": [
                        {"key": "jdbc_protocol", "value": "_jdbc_protocol_"},
                        {"key": "original_id", "value": "key"},
                        {"key": "host_", "value": "_jdbc_host_"},
                        {"key": "port_", "value": "_jdbc_port_"},
                        {"key": "database_", "value": "_jdbc_database_"},
                        {"key": "id_prefix", "value": "database_"},
                    ],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_concept(data_db_agg, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            nodes.extend(res["nodes"])
            data_db["generic_key"] = "generic_database"

        # add generic database structure
        nodes.append(
            {
                "id": "generic_database",
                "type": ElementType.DATA_OBJECT,
                "name": "database",
                "label": "database",
            }
        )
        nodes.append(
            {"id": "generic_table", "type": ElementType.DATA_OBJECT, "name": "table", "label": "table"}
        )
        edges.append(
            {
                "id": "generic_table_generic_database",
                "type": RelationshipType.AGGREGATION,
                "target": "generic_table",
                "source": "generic_database",
                "name": "",
                "label": "",
            }
        )

        # URLs
        if "data_url" in locals() and len(data_url) > 0:
            ids = [
                {
                    "prefix": "url_",
                    "id_key": "key",
                    "concept_name_prefix": "URL ",
                    "concept_name_key": "name",
                    "concept_label_prefix": "URL ",
                    "concept_label_key": "name",
                    "concept_type": ElementType.APPLICATION_INTERFACE,
                    "mapping": [
                        {"key": "original_id", "value": "id"},
                        {"key": "id_prefix", "value": "url_"},
                        {"key": "related_concept", "value": "id"},
                    ],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_concept(data_url, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            nodes.extend(res["nodes"])

        # IP Connections
        if "data_ip" in locals() and len(data_ip) > 0:
            ids = [
                {
                    "prefix": "ip_",
                    "id_key": "key",
                    "concept_name_prefix": "IP Connection ",
                    "concept_name_key": "name",
                    "concept_label_prefix": "IP Connection ",
                    "concept_label_key": "name",
                    "concept_type": ElementType.APPLICATION_INTERFACE,
                    "mapping": [
                        {"key": "original_id", "value": "id"},
                        {"key": "id_prefix", "value": "ip_"},
                        {"key": "related_concept", "value": "id"},
                    ],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_concept(data_ip, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            nodes.extend(res["nodes"])

        # tables
        # data = nodes_df.loc[nodes_df['_table_'].nonzero()]
        # data = data[data['_table_']!='[]']
        # TO BE DONE

        # %%
        #############################################################
        # edges
        model.nodes = pd.DataFrame(nodes)

        # edges related to core elements
        ids = [
            {
                "prefix": "nifi_nifi_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.TRIGGERING,
                "source_prefix": "nifi_",
                "source_id_key": "source",
                "target_prefix": "nifi_",
                "target_id_key": "target",
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "relationship", "value": "relationship"},
                ],
            },
            {
                "prefix": "nifi_nifi_queue_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.ACCESS_READ,
                "source_prefix": "nifi_",
                "source_id_key": "target",
                "target_prefix": "nifi_queue_",
                "target_id_key": "id",
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "relationship", "value": "relationship"},
                ],
            },
            {
                "prefix": "nifi_queue_nifi_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.ACCESS_WRITE,
                "source_prefix": "nifi_",
                "source_id_key": "source",
                "target_prefix": "nifi_queue_",
                "target_id_key": "id",
                "mapping": [
                    {"key": "original_id", "value": "id"},
                    {"key": "relationship", "value": "relationship"},
                ],
            },
        ]
        res = ExtractorLanguagePrimitives.parse_relationship(
            connection_df, model, ids, script_name, data_only
        )
        element_metadata.extend(res["metadata"])
        edges.extend(res["edges"])

        # edges derived from references to other concepts in the properties
        if "prop_conn_df" in locals() and len(prop_conn_df) > 0:
            ids = [
                {
                    "prefix": "nifi_prop_conn_",
                    "id_key": "id",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.SERVING,
                    "source_prefix": "nifi_",
                    "source_id_key": "target",
                    "target_prefix": "nifi_",
                    "target_id_key": "source",
                    "mapping": [
                        {"key": "original_id", "value": "id"},
                        {"key": "source_column", "value": "source_column"},
                    ],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(
                prop_conn_df, model, ids, script_name, data_only
            )
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

        # edges representing hierarchical relations of process groups
        data = pd.concat([nodes_df[["id", "parent"]], controller_service_df[["id", "parent"]], port_df])
        data = data[["id", "parent"]]
        data = data.reset_index()
        data = data.loc[data.parent.nonzero()]
        ids = [
            {
                "prefix": "nifi_hierarchy_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.AGGREGATION,
                "source_prefix": "nifi_",
                "source_id_key": "parent",
                "target_prefix": "nifi_",
                "target_id_key": "id",
                "mapping": [{"key": "original_id", "value": "id"}],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_relationship(data, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        edges.extend(res["edges"])

        data = connection_df.loc[connection_df.parent.nonzero()]
        ids = [
            {
                "prefix": "nifi_hierarchy_",
                "id_key": "id",
                "relationship_name_prefix": "",
                "relationship_name_key": "",
                "relationship_label_prefix": "",
                "relationship_label_key": "",
                "relationship_type": RelationshipType.AGGREGATION,
                "source_prefix": "nifi_",
                "source_id_key": "parent",
                "target_prefix": "nifi_queue_",
                "target_id_key": "id",
                "mapping": [{"key": "original_id", "value": "id"}],
            }
        ]
        res = ExtractorLanguagePrimitives.parse_relationship(data, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        edges.extend(res["edges"])

        # edges related to data objects
        if "data_db" in locals() and len(data_db) > 0:
            ids = [
                {
                    "prefix": "nifi_jdbc_database_",
                    "id_key": "id",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_READ_WRITE,
                    "source_prefix": "nifi_jdbc_",
                    "source_id_key": "id",
                    "target_prefix": "database_",
                    "target_id_key": "key",
                    "mapping": [],
                },
                {
                    "prefix": "nifi_nifi_jdbc_",
                    "id_key": "id",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.SERVING,
                    "source_prefix": "nifi_",
                    "source_id_key": "id",
                    "target_prefix": "nifi_jdbc_",
                    "target_id_key": "id",
                    "mapping": [],
                },
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(data_db, model, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

            # edges related to data objects
            ids = [
                {
                    "prefix": "database_generic_database_",
                    "id_key": "key",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.SPECIALIZATION,
                    "source_prefix": "database_",
                    "source_id_key": "key",
                    "target_prefix": "",
                    "target_id_key": "generic_key",
                    "mapping": [],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(
                data_db_agg, model, ids, script_name, data_only
            )
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

        # mapping specific table concepts to generic table concept
        # mapping aggregation relation between database and table
        if "mapping_agg_jdbc_table" in locals() and len(mapping_agg_jdbc_table) > 0:
            ids = [
                {
                    "prefix": "table_generic_table_",
                    "id_key": "key",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.SPECIALIZATION,
                    "source_prefix": "table_",
                    "source_id_key": "key",
                    "target_prefix": "",
                    "target_id_key": "generic_key",
                    "mapping": [],
                },
                {
                    "prefix": "database_table_",
                    "id_key": "key",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.AGGREGATION,
                    "source_prefix": "database_",
                    "source_id_key": "_jdbc_key_",
                    "target_prefix": "table_",
                    "target_id_key": "key",
                    "mapping": [],
                },
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(
                mapping_agg_jdbc_table, model, ids, script_name, data_only
            )
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

            # relation between specific table object and the processor executing the access
            # relation between concept defining the query
            # relation between query executor and query
            ids = [
                {
                    "prefix": "nifi_table_",
                    "id_key": "_query_executor_",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_READ_WRITE,
                    "source_prefix": "nifi_",
                    "source_id_key": "_query_executor_",
                    "target_prefix": "table_",
                    "target_id_key": "key",
                    "mapping": [],
                },
                {
                    "prefix": "nifi_nifi_query_write_",
                    "id_key": "id",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_WRITE,
                    "source_prefix": "nifi_",
                    "source_id_key": "group",
                    "target_prefix": "nifi_query_",
                    "target_id_key": "id",
                    "mapping": [],
                },
                {
                    "prefix": "nifi_nifi_query_read_",
                    "id_key": "_query_executor_",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_READ,
                    "source_prefix": "nifi_",
                    "source_id_key": "_query_executor_",
                    "target_prefix": "nifi_query_",
                    "target_id_key": "id",
                    "mapping": [],
                },
                {
                    "prefix": "nifi_nifi_query_read_",
                    "id_key": "_query_executor_",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_READ_WRITE,
                    "source_prefix": "nifi_",
                    "source_id_key": "_query_executor_",
                    "target_prefix": "nifi_jdbc_",
                    "target_id_key": "_service_id_",
                    "mapping": [],
                },
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(
                mapping_agg_jdbc, model, ids, script_name, data_only
            )
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

        # edges related to urls
        if "data_url" in locals() and len(data_url) > 0:
            ids = [
                {
                    "prefix": "nifi_url_",
                    "id_key": "id",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_READ_WRITE,
                    "source_prefix": "nifi_",
                    "source_id_key": "id",
                    "target_prefix": "url_",
                    "target_id_key": "key",
                    "mapping": [],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(data_url, model, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

        # edges related to ip connections
        if "data_ip" in locals() and len(data_ip) > 0:
            ids = [
                {
                    "prefix": "nifi_ip_",
                    "id_key": "id",
                    "relationship_name_prefix": "",
                    "relationship_name_key": "",
                    "relationship_label_prefix": "",
                    "relationship_label_key": "",
                    "relationship_type": RelationshipType.ACCESS_READ_WRITE,
                    "source_prefix": "nifi_",
                    "source_id_key": "id",
                    "target_prefix": "ip_",
                    "target_id_key": "key",
                    "mapping": [],
                }
            ]
            res = ExtractorLanguagePrimitives.parse_relationship(data_ip, model, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            edges.extend(res["edges"])

        # %%
        #############################################################
        # view
        model.edges = pd.DataFrame(edges)
        model.organize()

        node_lookup = pd.concat([nodes_df[["id", "x", "y"]], port_df])
        node_lookup = node_lookup[["id", "x", "y"]]
        node_lookup = node_lookup.set_index("id")
        inter = connection_df.merge(node_lookup, how="left", left_on="source", right_index=True)
        inter = inter.merge(node_lookup, how="left", left_on="target", right_index=True)
        inter["x"] = inter.apply(lambda x: (min(x["x_x"], x["x_y"]) + max(x["x_x"], x["x_y"])) / 2, axis=1)
        inter["y"] = inter.apply(lambda x: (min(x["y_x"], x["y_y"]) + max(x["y_x"], x["y_y"])) / 2, axis=1)

        # data = connection_df[['id','groupId','parent','parentGroupId','path']].copy()
        data = inter[["id", "groupId", "parent", "parentGroupId", "path", "x", "y"]].copy()
        data["width"] = 0
        data["height"] = 0
        data["name"] = None
        data = data.rename(index=str, columns={"id": "con_id"})
        # data.columns=['con_id','groupId','parent','parentGroupId','path','x','y','width','height','name']
        data = pd.concat([data, nodes_df[["id", "groupId", "parent", "parentGroupId", "path", "x", "y"]]])
        if "port_df" in locals() and len(port_df) > 0:
            data = pd.concat([data, port_df[["id", "groupId", "parent", "parentGroupId", "path", "x", "y"]]])
        data = data.rename(index=str, columns={"id": "node_id"})
        # data.columns = ['con_id', 'groupId','node_id', 'parent',
        #    'parentGroupId', 'path', 'x', 'y','width','height','name']
        data["id"] = None
        if "label_df" in locals() and len(label_df) > 0:
            data = pd.concat(
                [
                    data,
                    label_df[
                        [
                            "id",
                            "groupId",
                            "parent",
                            "parentGroupId",
                            "path",
                            "x",
                            "y",
                            "width",
                            "height",
                            "name",
                        ]
                    ],
                ]
            )
            # data= data[['id','groupId','parent','parentGroupId','path','x','y','width','height','name']]
        data = data.reset_index()
        data["view_name"] = data["path"].apply(lambda x: x[-1])
        data["path2"] = data["path"].apply(lambda x: x[0:-1])
        # data['name']

        ids = [
            {
                "id_type": "dynamic",
                "id_prefix": "nifi_process_group_",
                "id_key": "groupId",
                "view_name_type": "dynamic",
                "view_name_prefix": "",
                "view_name_key": "view_name",
                "view_path": [
                    {"type": "static", "value": "nifi"},
                    {"type": "static", "value": "process groups and templates"},
                    {"type": "dynamic", "prefix": "", "value": "path2"},
                ],
                "view_nodes": [
                    {"id_prefix": "nifi_", "id_key": "node_id", "x_key": "x", "y_key": "y"},
                    {"id_prefix": "nifi_queue_", "id_key": "con_id", "x_key": "x", "y_key": "y"},
                ],
                "view_edges": [
                    {"id_prefix": "nifi_nifi_", "id_key": "con_id"},
                    {"id_prefix": "nifi_queue_nifi_", "id_key": "con_id"},
                    {"id_prefix": "nifi_nifi_queue_", "id_key": "con_id"},
                    {"id_prefix": "nifi_hierarchy_", "id_key": "con_id"},
                    {"id_prefix": "nifi_hierarchy_", "id_key": "node_id"},
                ],
                "view_labels": [
                    {
                        "id_prefix": "nifi_",
                        "id_key": "id",
                        "x_key": "x",
                        "y_key": "y",
                        "width_key": "width",
                        "height_key": "height",
                        "name_key": "name",
                    }
                ],
                "view_layout": Layout.MANUAL,
            }
        ]
        res = ExtractorLanguagePrimitives.parse_view(data, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        views.extend(res["views"])

        data = prop_conn_df.copy()
        # ll = list(data.target.unique())
        # data2 = connection_df[np.isin(model.edges.id,ll) ]
        # data2 = connection_df[np.isin(edges_df.source,ll) ]
        # data['key'] = data.id
        ids = [
            {
                "id_type": "dynamic",
                "id_prefix": "nifi_services_",
                "id_key": "source_column",
                "view_name_type": "dynamic",
                "view_name_prefix": "property ",
                "view_name_key": "source_column",
                "view_path": [
                    {"type": "static", "value": "nifi"},
                    {"type": "static", "value": "service mapping"},
                ],
                "view_nodes": [
                    {"id_prefix": "nifi_", "id_key": "source"},
                    {"id_prefix": "nifi_", "id_key": "target"},
                ],
                "view_edges": [
                    {"id_prefix": "nifi_", "id_key": "id"},
                    {"id_prefix": "nifi_prop_conn_", "id_key": "id"},
                ],
                "view_layout": Layout.HIERARCHICAL,
            }
        ]
        res = ExtractorLanguagePrimitives.parse_view(data, model, ids, script_name, data_only)
        element_metadata.extend(res["metadata"])
        views.extend(res["views"])

        if "mapping_df" in locals() and len(mapping_df) > 0:
            data = mapping_df.copy()
            data["group"] = data.group.apply(lambda x: x[0])
            data2 = data_queries[["id", "_query_", "_table_", "_query_type_"]].copy()
            data2["_table_"] = data2._table_.apply(lambda x: x[0])
            data2["view_name"] = data2.apply(
                lambda x: "{} {}".format(x["_table_"], x["_query_type_"][0]), axis=1
            )
            data = data.merge(
                data2[["id", "_query_", "_table_", "view_name"]], how="left", left_on="group", right_on="id"
            )
            data["table_key"] = data.apply(lambda x: "{}_{}".format(x["_jdbc_key_"], x["_table_"]), axis=1)
            # ll = list(data.target.unique())
            # data2 = connection_df[np.isin(model.edges.id,ll) ]
            # data2 = connection_df[np.isin(edges_df.source,ll) ]
            # data['key'] = data.id
            ids = [
                {
                    "id_type": "dynamic",
                    "id_prefix": "nifi_query_processing_",
                    "id_key": "group",
                    "view_name_type": "dynamic",
                    "view_name_prefix": "query ",
                    "view_name_key": "view_name",
                    "view_path": [
                        {"type": "static", "value": "nifi"},
                        {"type": "static", "value": "query processing"},
                    ],
                    "view_nodes": [
                        {"id_prefix": "nifi_", "id_key": "id_x"},
                        {"id_prefix": "nifi_query_", "id_key": "id_x"},
                        {"id_prefix": "database_", "id_key": "_jdbc_key_"},
                        {"id_prefix": "nifi_", "id_key": "_query_executor_"},
                        {"id_prefix": "table_", "id_key": "table_key"},
                        {"id_prefix": "nifi_jdbc_", "id_key": "id_x"},
                    ],
                    "view_layout": Layout.HIERARCHICAL,
                }
            ]
            res = ExtractorLanguagePrimitives.parse_view(data, model, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            views.extend(res["views"])

            ids = [
                {
                    "id_type": "dynamic",
                    "id_prefix": "nifi_data_model_",
                    "id_key": "_jdbc_key_",
                    "view_name_type": "dynamic",
                    "view_name_prefix": "database ",
                    "view_name_key": "_jdbc_key_",
                    "view_path": [
                        {"type": "static", "value": "nifi"},
                        {"type": "static", "value": "data model"},
                    ],
                    "view_nodes": [
                        {"id_prefix": "database_", "id_key": "_jdbc_key_"},
                        {"id_prefix": "table_", "id_key": "key"},
                    ],
                    "view_edges": [{"id_prefix": "database_table_", "id_key": "key"}],
                    "view_layout": Layout.HIERARCHICAL,
                }
            ]
            res = ExtractorLanguagePrimitives.parse_view(
                mapping_agg_jdbc_table, model, ids, script_name, data_only
            )
            element_metadata.extend(res["metadata"])
            views.extend(res["views"])

        if "data_url" in locals() and len(data_url) > 0:
            ids = [
                {
                    "id_type": "dynamic",
                    "id_prefix": "nifi_url_processing_",
                    "id_key": "key",
                    "view_name_type": "dynamic",
                    "view_name_prefix": "URL ",
                    "view_name_key": "name",
                    "view_path": [{"type": "static", "value": "nifi"}, {"type": "static", "value": "URLs"}],
                    "view_nodes": [
                        {"id_prefix": "nifi_", "id_key": "id"},
                        {"id_prefix": "url_", "id_key": "key"},
                    ],
                    "view_layout": Layout.HIERARCHICAL,
                }
            ]
            res = ExtractorLanguagePrimitives.parse_view(data_url, model, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            views.extend(res["views"])

        if "data_ip" in locals() and len(data_ip) > 0:
            ids = [
                {
                    "id_type": "dynamic",
                    "id_prefix": "nifi_ip_processing_",
                    "id_key": "key",
                    "view_name_type": "dynamic",
                    "view_name_prefix": "IP Connection ",
                    "view_name_key": "name",
                    "view_path": [
                        {"type": "static", "value": "nifi"},
                        {"type": "static", "value": "IP Connections"},
                    ],
                    "view_nodes": [
                        {"id_prefix": "nifi_", "id_key": "id"},
                        {"id_prefix": "ip_", "id_key": "key"},
                    ],
                    "view_layout": Layout.HIERARCHICAL,
                }
            ]
            res = ExtractorLanguagePrimitives.parse_view(data_ip, model, ids, script_name, data_only)
            element_metadata.extend(res["metadata"])
            views.extend(res["views"])
        # %%
        return {"model": model, "data": element_metadata}


# %%
#        model_options = {
#                'projectOwner': 'dev',
#                'projectName': 'test_resin_1171',
#                }

#        branch_name = 'nifi'
#        model.name = 'monitoring model'

# upload the model to the repository
#        res2 = ArchimateUtils.commit_model_to_repository(
#            model, branchName=branch_name, userid='dev',
#            description='monitoring model', **model_options)
# %%
#        res3 = PlatformUtils.upload_model_data(
#            branchName=branch_name, conceptData=element_metadata,
#            **model_options)

# END of method
