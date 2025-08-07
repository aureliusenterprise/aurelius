# Kafka Topics

This page describes how Kafka topics are managed.

## What is a Kafka Topic?

A Kafka topic is a category or feed name to which events are published by producers. Consumers can subscribe
to these topics to receive events. Topics are used to organize and categorize events in Kafka. Each topic
is identified by a unique name. See the [naming conventions](#naming-conventions) for more information on
how topics are named.

## Partitioning

A Kafka topic is divided into partitions. Partitions allow events to be distributed across multiple brokers
in a Kafka cluster, which facilitates scalability and fault tolerance. Each partition is an ordered, immutable
sequence of events that is assigned a unique identifier called the partition ID. events within a partition
are assigned an offset, which is a unique identifier that represents the position of the event within the
partition.

??? QUESTION "How many partitions should I use?"

    The number of partitions for a topic depends on the expected volume of events and the number of consumers
    that will be reading from the topic. A good rule of thumb is to start with a small number of partitions
    (e.g., 1-3) and increase the number as needed based on the performance and scalability requirements.

    More partitions allow for greater parallelism, but also increase the complexity of managing the topic.
    A common practice is to start with a number of partitions that is a multiple of the number of consumers
    that will be reading from the topic. This ensures that each consumer can read from at least one partition
    and helps to balance the load across consumers.

## Offsets

An offset is a unique identifier that represents the position of a event within a partition. Offsets are used
by consumers to keep track of the events they have read. When a consumer reads a event from a partition, it
commits the offset of the last event it has read. This allows the consumer to resume reading from the same
position if it is restarted.

Alternatively, a consumer can choose to read events from a specific offset within a partition. This is useful
for scenarios where a consumer needs to reprocess events or skip events that have already been processed, or
if a consumer is starting for the first time and wants to read only new events.

## Data Retention

Kafka topics can be configured with a retention policy that determines how long events are retained in the
topic. events can be retained for a specific period of time or until a certain size threshold is reached. Once
the retention policy is met, events are deleted from the topic.

There are two main types of retention policies:

- **Time-based retention**: events are retained for a specific period of time, after which they are deleted.
- **Size-based retention**: events are retained until the topic reaches a certain size, after which the oldest
  events are deleted to make room for new events.

By default, Kafka topics are configured with a time-based retention policy of 7 days. This means that events
are retained for 7 days before they are deleted. You can configure the retention policy for a topic by setting
the `retention.ms` or `retention.bytes` configuration properties when creating the topic.

Kafka also supports log compaction, which is a process that retains only the latest version of each key in a topic.
This is useful for topics that contain events with unique keys, such as user profiles or configuration settings.
Compaction ensures that only the most recent event for each key is retained, while older events are deleted.
This helps reduce storage requirements and improves read performance for consumers that only need the latest state
of each key.

## Replication

To avoid data loss in the event of a broker failure, Kafka uses replication to create copies of partitions across
multiple brokers. Each partition has a leader and one or more followers. The leader is responsible for handling
read and write requests for the partition, while the followers replicate the data from the leader. If the leader
fails, one of the followers is elected as the new leader.

Replication is configured at the topic level, and you can specify the number of replicas for each partition
when creating a topic.

??? QUESTION "How many replicas should I use?"

    The number of replicas depends on the size of your Kafka cluster and your availability requirements. At a
    minimum, we recommend using a replication factor of 2, which ensures that there is one replica in addition
    to the leader. This provides basic fault tolerance in case of a broker failure.

    The replication factor can be changed later if necessary.

??? INFO "Maximum Replication Factor"

    The number of replicas cannot exceed the number of brokers in the cluster, so if you have 3 brokers, you can
    set the replication factor to 2 or 3.

## Schemas

We strongly recommends defining schemas for the data published on Kafka topics. Schemas provide a formal
definition of the structure of the data, which helps ensure that producers and consumers can interpret the data
correctly. Learn more about how schemas are used in the [schemas documentation](./schemas.md).

## Naming Conventions

Following these conventions will help ensure that kafka topic names are consistent, easy to read, and informative.

### Principles

The following principles guide the naming conventions for Kafka topics:

#### Keep Names Short and Descriptive

Use short, descriptive names for Kafka topics. Short names are easier to read and understand, while descriptive
names provide context and meaning. By combining these two principles, you can create names that are both concise
and informative.

As a general rule, names should not exceed 35 characters.

#### Ensure Consistency and Readability

Use `kebab-case` for Kafka topic names. Kebab case is a naming convention that uses strictly lower-case letters
and hyphens (`-`) to separate parts of a name. Following this convention keeps resource names consistent and easy
to read.

Components of a name should be separated by periods (`.`).

#### Don't use special characters

Avoid using special characters in Kafka topic names. Special characters can cause issues with system compatibility
and make names harder to read. Stick to letters, numbers, and hyphens. Avoid using characters with diacritics,
such as accents or umlauts.

### Name Components

The following components make up a the name of a Kafka topic:

#### Resource Category

You can group resources into categories to indicate their purpose or ownership. Categories help organize resources
and provide additional context. Categories should be short and descriptive, with a maximum of 10 characters.

#### Resource Description

Provide a description for the resource, limited to a maximum of 15 characters. Avoid dependencies between subsequent
processes in a pipeline. Choose names that accurately describe the function of the process or the meaning of the
data structure.

#### Versioning

If versioning is necessary, for example in case of a breaking schema change, use an incremental number to indicate
the version. The version number should be included as a suffix after the resource description.

Version numbers start at `v1` and increment by `1` for each new version. If no version number is specified, the
resource is considered to be version `v1`.

??? EXAMPLE "Versioning Example"

    A new version of a Kafka Topic `sales.orders` could be named `sales.orders.v2`.

Maintaining multiple versions of a resource should always be a temporary solution. A deprecation notice should
be issued and a migration path should be provided to consumers of the old version.

??? TIP "Prefer Schema Evolution"

    In most cases versioning can be avoided by using [schema evolution with the Schema Registry](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html).

    Schema evolution allows you to make changes to the schema of a data structure without breaking compatibility
    existing consumers. This approach is more flexible and easier to manage than maintaining multiple versions of
    a resource.

    Read more about schema evolution in the [schemas documentation](./schemas.md).

#### Environment Indicator

We choose not to include an environment indicator in resource names. This approach improves that configuration
portability between environments and thereby reduces the risk of errors.
