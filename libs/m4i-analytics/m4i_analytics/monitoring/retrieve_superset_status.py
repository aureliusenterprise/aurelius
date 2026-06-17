import re
from datetime import datetime

import requests
from pandas import DataFrame
from requests.auth import HTTPBasicAuth

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import RelationshipType
from m4i_analytics.graphs.model.Graph import EdgeAttribute, NodeAttribute
from m4i_analytics.m4i.platform.PlatformUtils import PlatformUtils
from m4i_analytics.m4i.portal.DBUtils import DBUtils, InsertBehavior

nagios_host = "http://www.models4insight.com/nagios/"
credentials = {"username": "nagiosadmin", "password": "aurelius17"}


class Status:
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    OK_PATTERN = re.compile(r"\bOK\b")
    WARNING_PATTERN = re.compile(r"\bWARNING\b")
    CRITICAL_PATTERN = re.compile(r"\bCRITICAL\b")

    @staticmethod
    def parse_status(status_string):
        result = Status.OK
        if Status.CRITICAL_PATTERN.search(status_string):
            result = Status.CRITICAL
        elif Status.WARNING_PATTERN.search(status_string):
            result = Status.WARNING
        return result

    # END parse_status


# END Status


def retrieve_superset_status(nagios_host, credentials, host_name, service_name):
    def get_objects(params):
        response = requests.get(
            f"http://{nagios_host}/nagios/cgi-bin/objectjson.cgi",
            params=params,
            auth=HTTPBasicAuth(credentials["username"], credentials["password"]),
        )
        response.raise_for_status()
        return response.json()

    # END get_objects

    def get_status(params):
        response = requests.get(
            f"http://{nagios_host}/nagios/cgi-bin/statusjson.cgi",
            params=params,
            auth=HTTPBasicAuth(credentials["username"], credentials["password"]),
        )
        response.raise_for_status()
        return response.json()

    # END get_objects

    def hostlist():
        """
        :returns: A list of all the known hostnames
        :rtype: list of str
        """

        params = {"query": "hostlist"}

        return get_objects(params)["data"]["hostlist"]

    # END hostlist

    def host(hostname):
        """
        :returns: The details for a particular host
        :rtype: dict
        """

        params = {"query": "host", "hostname": hostname}

        return get_objects(params)["data"]["host"]

    # END host

    def servicelist():
        """
        Returns a list of the names of the services available per host

        :returns: A dictionary containing lists of services available per host
        :rtype: dict

        :exception requests.exceptions.HTTPError: Thrown when the response
            returned with a HTTP 400/500 code variant.
        """

        params = {"query": "servicelist"}

        return get_objects(params)["data"]["servicelist"]

    # END servicelist

    def service(host, servicename):
        """
        :returns: The details for a particular service on a particular host
        :rtype: dict

        :param str host: The name of the host.
        :param str servicename: The name of the service.

        :exception requests.exceptions.HTTPError: Thrown when the response
            returned with a HTTP 400/500 code variant.
        """

        params = {"query": "service", "hostname": host, "servicedescription": servicename}

        return get_objects(params)["data"]["service"]

    # END service

    def service_output(host, servicename):
        """
        :returns: The current output for a particular service on a particular host
        :rtype: str

        :param str host: The name of the host.
        :param str servicename: The name of the service.

        :exception requests.exceptions.HTTPError: Thrown when the response
            returned with a HTTP 400/500 code variant.
        """

        params = {"query": "service", "hostname": host, "servicedescription": servicename}

        return get_status(params)["data"]["service"]["long_plugin_output"]

    # END service_output

    def service_status(host, servicename):
        """
        :returns: The current status for a particular service on a particular host
        :rtype: Status

        :param str host: The name of the host.
        :param str servicename: The name of the service.

        :exception requests.exceptions.HTTPError: Thrown when the response
            returned with a HTTP 400/500 code variant.
        """

        return Status.parse_status(service_output(host, servicename))

    # END service_status

    def current_service_health():
        services_per_host = servicelist()

        return [
            {"host": host, "service": service, "status": service_status(host, service)}
            for host in services_per_host
            for service in services_per_host[host]
        ]

    # END current_service_health

    def update_events(host, servicename):
        result = []
        request_path_pattern = re.compile(r'http://.+?(?::\d+/|\.\w+)(.+?)"')
        entity_id_pattern = re.compile(r"/(\d+?)(?:/|$)")
        slice_id_pattern = re.compile(r"slice_id%22%3A(\d+?)%")

        event = service_output(host, servicename)
        event_status = Status.parse_status(event)

        if event_status != Status.OK:
            request_paths = re.findall(request_path_pattern, event)

            # Handle superset requests
            superset_paths = [address for address in request_paths if "superset" in address]

            table_ids = [
                f"table-{identifier}"
                for path in superset_paths
                if "table" in path and "slice" not in path
                for identifier in re.findall(entity_id_pattern, path)
            ]
            slice_ids = [
                f"slice-{identifier}"
                for path in superset_paths
                if "table" in path and "slice" in path
                for identifier in re.findall(slice_id_pattern, path)
            ]
            dashboard_ids = [
                f"dashboard-{identifier}"
                for path in superset_paths
                if "dashboard" in path
                for identifier in re.findall(entity_id_pattern, path)
            ]

            concept_data = (
                [
                    {
                        "id": table_id,
                        "data": {
                            "apache_vhosts": {
                                Status.OK: len([t for t in table_ids if t == table_id])
                                if event_status == Status.OK
                                else 0,
                                Status.WARNING: len([t for t in table_ids if t == table_id])
                                if event_status == Status.WARNING
                                else 0,
                                Status.CRITICAL: len([t for t in table_ids if t == table_id])
                                if event_status == Status.CRITICAL
                                else 0,
                            }
                        },
                    }
                    for table_id in list(set(table_ids))
                ]
                + [
                    {
                        "id": slice_id,
                        "data": {
                            "apache_vhosts": {
                                Status.OK: len([s for s in slice_ids if s == slice_id])
                                if event_status == Status.OK
                                else 0,
                                Status.WARNING: len([s for s in slice_ids if s == slice_id])
                                if event_status == Status.WARNING
                                else 0,
                                Status.CRITICAL: len([s for s in slice_ids if s == slice_id])
                                if event_status == Status.CRITICAL
                                else 0,
                            }
                        },
                    }
                    for slice_id in list(set(slice_ids))
                ]
                + [
                    {
                        "id": dashboard_id,
                        "data": {
                            "apache_vhosts": {
                                Status.OK: len([d for d in dashboard_ids if d == dashboard_id])
                                if event_status == Status.OK
                                else 0,
                                Status.WARNING: len([d for d in dashboard_ids if d == dashboard_id])
                                if event_status == Status.WARNING
                                else 0,
                                Status.CRITICAL: len([d for d in dashboard_ids if d == dashboard_id])
                                if event_status == Status.CRITICAL
                                else 0,
                            }
                        },
                    }
                    for dashboard_id in list(set(dashboard_ids))
                ]
            )

            if len(concept_data) > 0:
                result = concept_data
        return result

    # END events_with_context

    return update_events(host_name, service_name)


# END retrieve_superset_status


def update_status(model=None, dataset=None, model_options=None):
    if model_options is None:
        model_options = {}
    if not model:
        model = ArchimateUtils.load_model_from_repository(userid="thijsfranck", **model_options)

    if not dataset:
        dataset = PlatformUtils.retrieve_data(**model_options)

    concepts_with_events = [
        {"id": concept.id, "events": concept.data["apache_vhosts"]}
        for concept in dataset.content  # type: ignore[reportGeneralTypeIssues]
        if concept.data and concept.data.get("events")
    ]

    abstract_table_id = next(
        node[model.getNodeAttributeMapping(NodeAttribute.ID)]
        for node in model.nodes.to_dict(orient="records")
        if node[model.getNodeAttributeMapping(NodeAttribute.NAME)] == "table"
    )
    abstract_dashboard_id = next(
        node[model.getNodeAttributeMapping(NodeAttribute.ID)]
        for node in model.nodes.to_dict(orient="records")
        if node[model.getNodeAttributeMapping(NodeAttribute.NAME)] == "dashboard"
    )
    abstract_slice_id = next(
        node[model.getNodeAttributeMapping(NodeAttribute.ID)]
        for node in model.nodes.to_dict(orient="records")
        if node[model.getNodeAttributeMapping(NodeAttribute.NAME)] == "slice"
    )

    table_ids = [
        edge[model.getEdgeAttributeMapping(EdgeAttribute.TARGET)]
        for edge in model.edges.to_dict(orient="records")
        if edge[model.getEdgeAttributeMapping(EdgeAttribute.TYPE)] == RelationshipType.SPECIALIZATION
        and edge[model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)] == abstract_table_id
    ]
    dashboard_ids = [
        edge[model.getEdgeAttributeMapping(EdgeAttribute.TARGET)]
        for edge in model.edges.to_dict(orient="records")
        if edge[model.getEdgeAttributeMapping(EdgeAttribute.TYPE)] == RelationshipType.SPECIALIZATION
        and edge[model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)] == abstract_dashboard_id
    ]
    slice_ids = [
        edge[model.getEdgeAttributeMapping(EdgeAttribute.TARGET)]
        for edge in model.edges.to_dict(orient="records")
        if edge[model.getEdgeAttributeMapping(EdgeAttribute.TYPE)] == RelationshipType.SPECIALIZATION
        and edge[model.getEdgeAttributeMapping(EdgeAttribute.SOURCE)] == abstract_slice_id
    ]

    def fmt_event(event):
        result = 0
        if event[Status.CRITICAL]:
            result = 3
        elif event[Status.WARNING]:
            result = 2
        elif event[Status.OK]:
            result = 1
        return {"apache_vhosts": {"data_in": 0, "service": result, "processing": 0, "data_out": 0}}

    # END fmt_event

    table_status = [
        {
            "id": table,
            "type": "table",
            "status": {"apache_vhosts": {"data_in": 0, "service": 1, "processing": 0, "data_out": 0}}
            if table not in [concept["id"] for concept in concepts_with_events]
            else next(
                fmt_event(concept["events"]) for concept in concepts_with_events if concept["id"] == table
            ),
        }
        for table in table_ids
    ]
    dashboard_status = [
        {
            "id": dashboard,
            "type": "dashboard",
            "status": {"apache_vhosts": {"data_in": 0, "service": 1, "processing": 0, "data_out": 0}}
            if dashboard not in [concept["id"] for concept in concepts_with_events]
            else next(
                fmt_event(concept["events"]) for concept in concepts_with_events if concept["id"] == dashboard
            ),
        }
        for dashboard in dashboard_ids
    ]
    slice_status = [
        {
            "id": slice_id,
            "type": "slice",
            "status": {"apache_vhosts": {"data_in": 0, "service": 1, "processing": 0, "data_out": 0}}
            if slice_id not in [concept["id"] for concept in concepts_with_events]
            else next(
                fmt_event(concept["events"]) for concept in concepts_with_events if concept["id"] == slice_id
            ),
        }
        for slice_id in slice_ids
    ]

    concept_data = [
        {"id": obj["id"], "data": {"type": obj["type"], "status": obj["status"]}}
        for obj in table_status + dashboard_status + slice_status
    ]

    return concept_data


# END update_status


def update_dashboard(model_options):
    model = ArchimateUtils.load_model_from_repository(userid="thijsfranck", **model_options)
    dataset = PlatformUtils.retrieve_data(**model_options)

    def map_status(status):
        result = Status.OK
        if status[Status.CRITICAL] > 0:
            result = Status.CRITICAL
        elif status[Status.WARNING] > 0:
            result = Status.WARNING
        return result

    # END map_status

    def map_concept_name(identifier):
        return next(
            (
                node[model.getNodeAttributeMapping(NodeAttribute.NAME)]
                for node in model.nodes.to_dict(orient="records")
                if str(node[model.getNodeAttributeMapping(NodeAttribute.ID)]) == str(identifier)
            ),
            None,
        )

    # END map_concept_name

    concept_statuses = [
        {
            "id": concept.id,
            "type": concept.data.get("type"),
            "name": map_concept_name(concept.id),
            "status": map_status(concept.data["status"]),
            "timestamp": datetime.fromtimestamp(concept.start_date / 1000),
        }
        for concept in dataset.content  # type: ignore[reportGeneralTypeIssues]
        if concept.data and concept.data.get("status")
    ]

    df = DataFrame(concept_statuses)

    DBUtils.insert_dataset(df, "test_superset_status", InsertBehavior.REPLACE)


# END update_dashboard
