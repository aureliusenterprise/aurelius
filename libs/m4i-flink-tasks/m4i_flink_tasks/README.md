# Flink Tasks

The `flink_tasks` package contains all tasks that are used as part of the Flink
data processing pipeline of Aurelius Atlas.

## Structure

The `flink_tasks` package contains the following sub-packages:

- `flink_tasks.model`: Contains the data model of the Flink data processing pipeline.
- `flink_tasks.operations`: Contains the processing steps for the Flink data processing pipeline.

## Architecture

This section describes the architecture of the Flink data processing pipeline of Aurelius Atlas.

### Data Flow

The Flink data processing pipeline is based on the Flink Streaming API.
The pipeline is structured as follows:

```mermaid
graph TB

    subgraph Flink["Flink Tasks"]
        GetEntity["Get Entity"]
        PublishState["Publish State"]
        DetermineChange["Determine Change"]
        SynchronizeAppSearch["Synchronize App Search"]
    end

    GetEntity --> PublishState
    PublishState --> DetermineChange
    DetermineChange --> SynchronizeAppSearch
```

> **Note**: External dependencies are not shown in the diagram.

Below is a functional description of each processing step:

| Step                   | Description                                  |
| ---------------------- | -------------------------------------------- |
| `GetEntity`            | Retrieves full entity from Apache Atlas.     |
| `PublishState`         | Publishes new entity state to Kafka.         |
| `DetermineChange`      | Determines the change in entity state.       |
| `SynchronizeAppSearch` | Updates affected documents in Elasticsearch. |

### Module Structure

Every processing step is implemented as a separate module. The modules are structured as follows:

```mermaid
graph TB

    subgraph Module["Module"]
        direction TB
        EventHandlers["Event Handlers"]
        Processor["Processor"]
        Facade["Facade"]
    end

    EventHandlers --> Processor
    Processor --> Facade
```

The main interface for each processing step is the `Facade` component.
It is responsible for applying the `Processor` to a given input stream of events.
The `Facade` provides several output streams for connecting to other processing steps.
Every `Facade` must have a `main` output for the happy flow,
and can have additional outputs for error handling.
For convenience, every `Facade` has an `error` output for generic error handling.

The `Processor` component is responsible for processing a single event.
It is the main component of the processing step.
The `Processor` can use the `EventHandlers` component to handle the different types of events
that are received by the processing step.
