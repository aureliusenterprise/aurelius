from m4i_analytics.m4i.nifi.NifiApi import NifiApi
from m4i_analytics.m4i.platform.PlatformUtils import PlatformUtils

model_options = {
    "projectName": "testproject nifi 38029091",
    "projectOwner": "thijsfranck",
    "branchName": "MASTER",
    "modelId": "TRUNK",
}


class Status:
    UNKNOWN = 0
    OK = 1
    WARNING = 2
    CRITICAL = 3

    def __init__(self, source, data_in=UNKNOWN, service=UNKNOWN, processing=UNKNOWN, data_out=UNKNOWN):
        self.source = source
        self.data_in = data_in
        self.service = service
        self.processing = processing
        self.data_out = data_out

    # END __init__


# END status


def processor_data(processor):
    status = processor.status
    return {
        "id": "nifi_id-" + processor.id,
        "data": {
            "nifi": {
                "timestamp": status.statsLastRefreshed,
                "state": status.runStatus,
                "bytesRead": status.aggregateSnapshot.bytesIn,
                "bytesWritten": status.aggregateSnapshot.bytesOut,
                "flowFilesIn": status.aggregateSnapshot.flowFilesIn,
                "flowFilesOut": status.aggregateSnapshot.flowFilesOut,
                "tasksRun": status.aggregateSnapshot.taskCount,
                "tasksCompleted": status.aggregateSnapshot.tasks,
                "taskDuration": status.aggregateSnapshot.tasksDuration,
            }
        },
    }


# END processor_status


def connection_data(connection):
    status = connection.status
    return {
        "id": "nifi_queue_id-" + connection.id,
        "data": {
            "nifi": {
                "source": connection.sourceId,
                "target": connection.destinationId,
                "timestamp": status.statsLastRefreshed,
                "bytesRead": status.aggregateSnapshot.bytesIn,
                "bytesWritten": status.aggregateSnapshot.bytesOut,
                "bytesQueued": status.aggregateSnapshot.bytesQueued,
                "flowFilesIn": status.aggregateSnapshot.flowFilesIn,
                "flowFilesOut": status.aggregateSnapshot.flowFilesOut,
                "flowFilesQueued": status.aggregateSnapshot.flowFilesQueued,
            }
        },
    }


# END processor_status


def processor_status(processor_data):
    old_data = [
        obj
        for obj in PlatformUtils.retrieve_data(**model_options).content  # type: ignore[reportGeneralTypeIssues]
        if obj.data.get("original_id") in [processor["id"] for processor in processor_data]
    ]

    def assess_state(processor):
        states = {
            "paused": Status.WARNING,
            "stopped": Status.CRITICAL,
            "invalid": Status.CRITICAL,
            "running": Status.OK,
        }

        state = processor["data"]["nifi"]["state"].lower()
        result = states.get(state, Status.UNKNOWN)

        return Status(
            "run_state",
            service=result,
            processing=result
            if (state == "running" or state == "invalid")
            and (result == Status.CRITICAL or result == Status.OK)
            else Status.UNKNOWN,
        )

    # END assess_state

    def assess_completion(processor):
        result = Status.UNKNOWN

        try:
            old_processor = next(old for old in old_data if old.data["original_id"] == processor["id"])

            completion_ratio = (
                processor["data"]["nifi"]["tasksRun"] / processor["data"]["nifi"]["tasksCompleted"]
                if processor["data"]["nifi"]["tasksCompleted"] > 0
                else 1
            )
            old_completion_ratio = (
                old_processor.data["nifi"]["tasksRun"] / old_processor.data["nifi"]["tasksCompleted"]
                if old_processor.data["nifi"]["tasksCompleted"] > 0
                else 1
            )
            relative_completion_ratio = completion_ratio / old_completion_ratio

            if relative_completion_ratio < 0.9:
                result = Status.CRITICAL
            elif relative_completion_ratio < 0.95:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass

        return Status("task_completion", processing=result, data_out=result)

    # END assess_completion

    result = [
        {
            "id": processor["id"],
            "data": {
                "status": {
                    obj.source: {
                        "data_in": obj.data_in,
                        "service": obj.service,
                        "processing": obj.processing,
                        "data_out": obj.data_out,
                    }
                    for obj in [assess_state(processor), assess_completion(processor)]
                }
            },
        }
        for processor in processor_data
    ]

    return result


# END processor_status


def connection_status(connection_data):
    old_data = [
        obj
        for obj in PlatformUtils.retrieve_data(**model_options).content  # type: ignore[reportGeneralTypeIssues]
        if obj.data.get("original_id") in [connection["id"] for connection in connection_data]
    ]

    def assess_bytesread(connection):
        result = Status.UNKNOWN
        try:
            old_connection = next(old for old in old_data if old.data["original_id"] == connection["id"])

            bytesread_ratio = (
                connection["data"]["nifi"]["bytesRead"] / old_connection.data["nifi"]["bytesRead"]
                if old_connection.data["nifi"]["bytesRead"] > 0
                else 1
            )

            if bytesread_ratio < 0.5 or bytesread_ratio > 2:
                result = Status.CRITICAL
            elif bytesread_ratio < 0.75 or bytesread_ratio > 1.5:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass
        return Status("bytes_read", data_in=result)

    # END assess_bytesread

    def assess_flowfilesin(connection):
        result = Status.UNKNOWN
        try:
            old_connection = next(old for old in old_data if old.data["original_id"] == connection["id"])

            flowfilesin_ratio = (
                connection["data"]["nifi"]["flowFilesIn"] / old_connection.data["nifi"]["flowFilesIn"]
                if old_connection.data["nifi"]["flowFilesIn"] > 0
                else 1
            )

            if flowfilesin_ratio < 0.5 or flowfilesin_ratio > 2:
                result = Status.CRITICAL
            elif flowfilesin_ratio < 0.75 or flowfilesin_ratio > 1.5:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass
        return Status("flow_files_in", data_in=result)

    # END assess_flowfilesin

    def assess_bytesqueued(connection):
        result = Status.UNKNOWN
        try:
            old_connection = next(old for old in old_data if old.data["original_id"] == connection["id"])

            bytesqueued_ratio = (
                connection["data"]["nifi"]["bytesQueued"] / old_connection.data["nifi"]["bytesQueued"]
                if old_connection.data["nifi"]["bytesQueued"] > 0
                else 1
            )

            if bytesqueued_ratio < 0.5 or bytesqueued_ratio > 2:
                result = Status.CRITICAL
            elif bytesqueued_ratio < 0.75 or bytesqueued_ratio > 1.5:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass
        return Status("bytes_queued", processing=result, data_out=result)

    # END assess_bytesqueued

    def assess_flowfilesqueued(connection):
        result = Status.UNKNOWN
        try:
            old_connection = next(old for old in old_data if old.data["original_id"] == connection["id"])

            flowfilesqueued_ratio = (
                connection["data"]["nifi"]["flowFilesQueued"] / old_connection.data["nifi"]["flowFilesQueued"]
                if old_connection.data["nifi"]["flowFilesQueued"] > 0
                else 1
            )

            if flowfilesqueued_ratio < 0.5 or flowfilesqueued_ratio > 2:
                result = Status.CRITICAL
            elif flowfilesqueued_ratio < 0.75 or flowfilesqueued_ratio > 1.5:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass
        return Status("flow_files_queued", processing=result, data_out=result)

    # END assess_flowfilesqueued

    def assess_byteswritten(connection):
        result = Status.UNKNOWN
        try:
            old_connection = next(old for old in old_data if old.data["original_id"] == connection["id"])

            byteswritten_ratio = (
                connection["data"]["nifi"]["bytesWritten"] / old_connection.data["nifi"]["bytesWritten"]
                if old_connection.data["nifi"]["bytesWritten"] > 0
                else 1
            )

            if byteswritten_ratio < 0.5 or byteswritten_ratio > 2:
                result = Status.CRITICAL
            elif byteswritten_ratio < 0.75 or byteswritten_ratio > 1.5:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass
        return Status("bytes_written", data_out=result)

    # END assess_byteswritten

    def assess_flowfilesout(connection):
        result = Status.UNKNOWN
        try:
            old_connection = next(old for old in old_data if old.data["original_id"] == connection["id"])

            flowfilesout_ratio = (
                connection["data"]["nifi"]["flowFilesOut"] / old_connection.data["nifi"]["flowFilesOut"]
                if old_connection.data["nifi"]["flowFilesOut"] > 0
                else 1
            )

            if flowfilesout_ratio < 0.5 or flowfilesout_ratio > 2:
                result = Status.CRITICAL
            elif flowfilesout_ratio < 0.75 or flowfilesout_ratio > 1.5:
                result = Status.WARNING
            else:
                result = Status.OK
        except Exception:
            pass
        return Status("flow_files_out", data_out=result)

    # END assess_flowfilesout

    result = [
        {
            "id": connection["id"],
            "data": {
                "status": {
                    obj.source: {
                        "data_in": obj.data_in,
                        "service": obj.service,
                        "processing": obj.processing,
                        "data_out": obj.data_out,
                    }
                    for obj in [
                        assess_bytesread(connection),
                        assess_flowfilesin(connection),
                        assess_bytesqueued(connection),
                        assess_flowfilesqueued(connection),
                        assess_byteswritten(connection),
                        assess_flowfilesout(connection),
                    ]
                }
            },
        }
        for connection in connection_data
    ]

    return result


# END connection_status


def retrieve_nifi_status():
    root = NifiApi.retrieve_process_group("root")
    process_group_flow = (
        root.processGroupFlow  # type: ignore[reportGeneralTypeIssues]
        if hasattr(root, "processGroupFlow") and root.processGroupFlow is not None  # type: ignore[reportGeneralTypeIssues]
        else None
    )
    if process_group_flow is None:
        raise ValueError("No process group flow found")
    processors = [processor for processor in process_group_flow.flow.processors]
    connections = [connection for connection in process_group_flow.flow.connections]

    processor_datas = [processor_data(processor) for processor in processors]
    connection_datas = [connection_data(connection) for connection in connections]

    processor_statuses = processor_status(processor_datas)
    connection_statuses = connection_status(connection_datas)

    concept_data = processor_datas + connection_datas
    concept_statuses = processor_statuses + connection_statuses

    return {"data": concept_data, "status": concept_statuses}


# END retrieve_nifi_status
