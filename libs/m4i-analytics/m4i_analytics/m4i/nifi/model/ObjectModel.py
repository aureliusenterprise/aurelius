from m4i_analytics.shared.model.BaseModel import BaseModel


class Permissions(BaseModel):
    _fields = [("canRead", bool, False), ("canWrite", bool, False)]


# END Permissions


class Breadcrumb(BaseModel):
    _fields = [
        ("id", str, False),
        ("permissions", Permissions, False),
        ("versionedFlowState", str, False),
    ]


# END Breadcrumb


class Revision(BaseModel):
    _fields = [
        ("clientId", str, False),
        ("version", int, False),
        ("lastModifier", str, False),
    ]


# END Revision


class Position(BaseModel):
    _fields = [("x", int, False), ("y", int, False)]


# END Position


class Bulletin(BaseModel):
    _fields = [
        ("id", int, False),
        ("nodeAddress", str, False),
        ("category", str, False),
        ("groupId", str, False),
        ("sourceId", str, False),
        ("sourceName", str, False),
        ("level", str, False),
        ("message", str, False),
        ("timestamp", str, False),
    ]


# END Bulletin


class BulletinEntity(BaseModel):
    _fields = [
        ("id", int, False),
        ("groupId", str, False),
        ("sourceId", str, False),
        ("timestamp", str, False),
        ("nodeAddress", str, False),
        ("canRead", bool, False),
        ("bulletin", Bulletin, False),
    ]


# END BulletinEntity


class Variable(BaseModel):
    _fields = [("name", str, False)]


# END Variable


class VersionControlInformation(BaseModel):
    _fields = [
        ("groupId", str, False),
        ("registryId", str, False),
        ("registryName", str, False),
        ("bucketId", str, False),
        ("bucketName", str, False),
        ("flowId", str, False),
        ("flowName", str, False),
        ("flowDescription", str, False),
        ("version", int, False),
        ("state", str, False),
        ("stateExplanation", str, False),
    ]


# END VersionControlInformation


class Component(BaseModel):
    _fields = [
        ("id", str, False),
        ("versionedComponentId", str, False),
        ("parentGroupId", str, False),
        ("position", Position, False),
        ("name", str, False),
        ("comments", str, False),
        ("variables", Variable, False),
        ("versionControlInformation", VersionControlInformation, False),
        ("runningCount", int, False),
        ("stoppedCount", int, False),
        ("invalidCount", int, False),
        ("disabledCount", int, False),
        ("activeRemotePortCount", int, False),
        ("inactiveRemotePortCount", int, False),
        ("upToDateCount", int, False),
        ("locallyModifiedCount", int, False),
        ("syncFailureCount", int, False),
        ("inputPortCount", int, False),
        ("outputPortCount", int, False),
    ]


# END Component


class ProcessGroup(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", BulletinEntity, True),
        ("disconnectedNodeAcknowledged", bool, False),
    ]


# END ProcessGroup


class ProcessGroupStatus(BaseModel):
    _fields = [
        ("id", str, False),
        ("name", str, False),
        ("statsLastRefreshed", str, False),
    ]


# END ProcessGroupStatus


class ProcessGroupEntity(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", BulletinEntity, True),
        ("disconnectedNodeAcknowledged", bool, False),
        ("component", ProcessGroup, False),
        ("status", ProcessGroupStatus, False),
        ("runningCount", int, False),
        ("stoppedCount", int, False),
        ("invalidCount", int, False),
        ("disabledCount", int, False),
        ("activeRemotePortCount", int, False),
        ("inactiveRemotePortCount", int, False),
        ("versionedFlowState", str, False),
        ("upToDateCount", int, False),
        ("locallyModifiedCount", int, False),
        ("staleCount", int, False),
        ("locallyModifiedAndStaleCount", int, False),
        ("syncFailureCount", int, False),
        ("inputPortCount", int, False),
        ("outputPortCount", int, False),
    ]


# END ProcessGroup


class Bundle(BaseModel):
    _fields = [("group", str, False), ("artifact", str, False), ("version", str, False)]


# END Bundle


class Style(BaseModel):
    _fields = [("name", str, False)]


# END Style


class Relationship(BaseModel):
    _fields = [
        ("name", str, False),
        ("description", str, False),
        ("autoTerminate", bool, False),
    ]


# END Relationship


class Property(BaseModel):
    _fields = [("name", str, False)]


# END Property


class AllowableValue(BaseModel):
    _fields = [
        ("displayName", str, False),
        ("value", str, False),
        ("description", str, False),
    ]


# END AllowableValue


class AllowableValueEntity(BaseModel):
    _fields = [("allowableValue", AllowableValue, False), ("canRead", bool, False)]


# END AllowableValueEntity


class DescriptorName(BaseModel):
    _fields = [
        ("name", str, False),
        ("displayName", str, False),
        ("description", str, False),
        ("defaultValue", str, False),
        ("allowableValues", AllowableValueEntity, True),
        ("required", bool, False),
        ("sensitive", bool, False),
        ("dynamic", bool, False),
        ("supportsEl", bool, False),
        ("expressionLanguageScope", str, False),
        ("identifiesControllerService", str, False),
        ("identifiesControllerServiceBundle", Bundle, False),
    ]


# END DescriptorName


class Descriptor(BaseModel):
    _fields = [("name", str, False)]


# END Descriptor


class Config(BaseModel):
    _fields = [("properties", Property, False), ("descriptors", Descriptor, False)]


# END Config


class Task(BaseModel):
    _fields = [("name", str, False)]


# END Task


class SchedulingPeriod(BaseModel):
    _fields = [("name", str, False)]


# END SchedulingPeriod


class Processor(BaseModel):
    _fields = [
        ("id", str, False),
        ("versionedComponentId", str, False),
        ("parentGroupId", str, False),
        ("position", Position, False),
        ("name", str, False),
        ("type", str, False),
        ("bundle", Bundle, False),
        ("state", str, False),
        ("style", Style, False),
        ("relationships", Relationship, True),
        ("description", str, False),
        ("supportsParallelProcessing", bool, False),
        ("supportsEventDriven", bool, False),
        ("supportsBatching", bool, False),
        ("persistsState", bool, False),
        ("restricted", bool, False),
        ("deprecated", bool, False),
        ("executionNodeRestricted", bool, False),
        ("multipleVersionsAvailable", bool, False),
        ("inputRequirement", str, False),
        ("config", Config, False),
        ("schedulingPeriod", str, False),
        ("schedulingStrategy", str, False),
        ("executionNode", str, False),
        ("penaltyDuration", str, False),
        ("yieldDuration", str, False),
        ("bulletinLevel", str, False),
        ("runDurationMillis", int, False),
        ("concurrentlySchedulableTaskCount", int, False),
        ("autoTerminatedRelationships", str, True),
        ("comments", str, False),
        ("customUiUrl", str, False),
        ("lossTolerant", bool, False),
        ("annotationData", str, False),
        ("defaultConcurrentTasks", Task, False),
        ("defaultSchedulingPeriod", SchedulingPeriod, False),
    ]


# END Processor


class ProcessorStatusSnapshot(BaseModel):
    _fields = [
        ("id", str, False),
        ("groupId", str, False),
        ("name", str, False),
        ("type", str, False),
        ("runStatus", str, False),
        ("executionNode", str, False),
        ("bytesRead", str, False),
        ("bytesWritten", str, False),
        ("read", str, False),
        ("written", str, False),
        ("flowFilesIn", int, False),
        ("bytesIn", int, False),
        ("input", str, False),
        ("flowFilesOut", int, False),
        ("bytesOut", int, False),
        ("output", str, False),
        ("taskCount", int, False),
        ("tasksDurationNanos", int, False),
        ("tasks", str, False),
        ("tasksDuration", str, False),
        ("activeThreadCount", int, False),
        ("terminatedThreadCount", int, False),
    ]


# END ProcessorStatusSnapshot


class NodeProcessorStatusSnapshot(BaseModel):
    _fields = [
        ("nodeId", str, False),
        ("address", str, False),
        ("apiPort", int, False),
        ("statusSnapshot", ProcessorStatusSnapshot, False),
    ]


# END NodeProcessorStatusSnapshot


class ProcessorStatus(BaseModel):
    _fields = [
        ("groupId", str, False),
        ("id", str, False),
        ("name", str, False),
        ("type", str, False),
        ("runStatus", str, False),
        ("statsLastRefreshed", str, False),
        ("aggregateSnapshot", ProcessorStatusSnapshot, False),
        ("nodeSnapshots", NodeProcessorStatusSnapshot, True),
    ]


# END ProcessorStatus


class ProcessorEntity(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", Bulletin, True),
        ("disconnectedNodeAcknowledged", bool, False),
        ("component", Processor, False),
        ("inputRequirement", str, False),
        ("status", ProcessorStatus, False),
    ]


# END ProcessorEntity


class PortStatusSnapshot(BaseModel):
    _fields = [
        ("id", str, False),
        ("groupId", str, False),
        ("name", str, False),
        ("activeThreadCount", int, False),
        ("followFilesIn", int, False),
        ("bytesIn", int, False),
        ("input", str, False),
        ("flowFilesOut", int, False),
        ("bytesOut", int, False),
        ("output", str, False),
        ("transmitting", bool, False),
        ("runStatus", str, False),
    ]


# END PortSnapshotStatus


class NodePortStatusSnapshot(BaseModel):
    _fields = [
        ("nodeId", str, False),
        ("address", str, False),
        ("apiPort", int, False),
        ("statusSnapshot", PortStatusSnapshot, False),
    ]


# END NodePortStatusSnapshot


class PortStatus(BaseModel):
    _fields = [
        ("id", str, False),
        ("groupId", str, False),
        ("name", str, False),
        ("transmitting", bool, False),
        ("runStatus", str, False),
        ("statsLastRefreshed", str, False),
        ("aggregateSnapshot", PortStatusSnapshot, False),
        ("nodeSnapshots", NodePortStatusSnapshot, True),
    ]


# END PortStatus


class Port(BaseModel):
    _fields = [
        ("id", str, False),
        ("versionedComponentId", str, False),
        ("parentGroupId", str, False),
        ("position", Position, False),
        ("name", str, False),
        ("comments", str, False),
        ("state", str, False),
        ("type", str, False),
        ("transmitting", bool, False),
        ("concurrentlySchedulableTaskCount", int, False),
        ("userAccessControl", str, True),
        ("groupAccessControl", str, True),
        ("validationErrors", str, True),
    ]


class PortEntity(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", Bulletin, True),
        ("disconnectedNodeAcknowledged", bool, False),
        ("status", PortStatus, False),
        ("portType", str, False),
    ]


# END Port


class ConnectionStatusSnapshot(BaseModel):
    _fields = [
        ("id", str, False),
        ("groupId", str, False),
        ("name", str, False),
        ("sourceId", str, False),
        ("sourceName", str, False),
        ("destinationId", str, False),
        ("destinationName", str, False),
        ("flowFilesIn", int, False),
        ("bytesIn", int, False),
        ("input", str, False),
        ("flowFilesOut", int, False),
        ("bytesOut", int, False),
        ("output", str, False),
        ("flowFilesQueued", int, False),
        ("bytesQueued", int, False),
        ("queued", str, False),
        ("queuedSize", str, False),
        ("queuedCount", str, False),
        ("percentUseCount", int, False),
        ("percentUseBytes", int, False),
    ]


# END ConnectionStatusSnapshot


class NodeConnectionStatusSnapshot(BaseModel):
    _fields = [
        ("nodeId", str, False),
        ("address", str, False),
        ("apiPort", int, False),
        ("statusSnapshot", ConnectionStatusSnapshot, False),
    ]


# END NodeConnectionStatusSnapshot


class ConnectionStatus(BaseModel):
    _fields = [
        ("id", str, False),
        ("groupid", str, False),
        ("name", str, False),
        ("statsLastRefreshed", str, False),
        ("sourceId", str, False),
        ("sourceName", str, False),
        ("destinationId", str, False),
        ("destinationName", str, False),
        ("aggregateSnapshot", ConnectionStatusSnapshot, False),
        ("nodeSnapshots", NodeConnectionStatusSnapshot, True),
    ]


# END ConnectionStatus


class Connectable(BaseModel):
    _fields = [
        ("id", str, False),
        ("versionedComponentId", str, False),
        ("type", str, False),
        ("groupId", str, False),
        ("name", str, False),
        ("running", bool, False),
        ("transmitting", bool, False),
        ("exists", bool, False),
        ("comments", str, False),
    ]


class Connection(BaseModel):
    _fields = [
        ("id", str, False),
        ("versionedComponentId", str, False),
        ("parentGroupId", str, False),
        ("position", str, False),
        ("source", Connectable, False),
        ("target", Connectable, False),
        ("name", str, False),
        ("labelIndex", int, False),
        ("getzIndex", int, False),
        ("selectedRelationships", str, True),
        ("availableRelationships", str, True),
        ("backPressureObjectThreshold", int, False),
        ("backPressureDataSizeThreshold", str, False),
        ("flowFileExpiration", str, False),
        ("prioritizers", str, True),
        ("bends", Position, True),
    ]


class ConnectionEntity(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", Bulletin, True),
        ("disconnectedNodeAcknowledged", bool, False),
        ("component", Connection, False),
        ("status", ConnectionStatus, False),
        ("bends", Position, True),
        ("labelIndex", int, False),
        ("getzIndex", int, False),
        ("sourceId", str, False),
        ("sourceGroupId", str, False),
        ("sourceType", str, False),
        ("destinationId", str, False),
        ("destinationGroupId", str, False),
        ("destinationType", str, False),
    ]


# END Connection


class Dimensions(BaseModel):
    _fields = [("width", int, False), ("height", int, False)]


# END Dimensions


class Label(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", Bulletin, True),
        ("disconnectedNodeAcknowledged", bool, False),
        ("dimensions", Dimensions, False),
    ]


# END Label


class Funnel(BaseModel):
    _fields = [
        ("revision", Revision, False),
        ("id", str, False),
        ("uri", str, False),
        ("position", Position, False),
        ("permissions", Permissions, False),
        ("bulletins", Bulletin, True),
        ("disconnectedNodeAcknowledged", bool, False),
    ]


# END Funnel


class Flow(BaseModel):
    _fields = [
        ("processGroups", ProcessGroupEntity, True),
        ("remoteProcessGroups", ProcessGroupEntity, True),
        ("processors", ProcessorEntity, True),
        ("inputPorts", PortEntity, True),
        ("outputPorts", PortEntity, True),
        ("connections", ConnectionEntity, True),
        ("labels", Label, True),
        ("funnels", Funnel, True),
    ]


# END Flow


class ProcessGroupFlow(BaseModel):
    _fields = [
        ("id", str, False),
        ("uri", str, False),
        ("parentGroupId", str, False),
        ("breadcrumb", Breadcrumb, False),
        ("flow", Flow, False),
        ("lastRefreshed", str, False),
    ]


# END ProcessGroupFlow


class ProcessGroupFlowEntity(BaseModel):
    _fields = [
        ("permissions", Permissions, False),
        ("processGroupFlow", ProcessGroupFlow, False),
    ]


# END ProcessGroupFlowEntity
