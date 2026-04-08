# aurelius-kafka-connect-jdbc-sink-base

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-kafka-connect-jdbc-sink-base&metric=sqale_rating&token=a5bcd9f548c5528522d96d7f0296b0336349e65e)](https://sonarcloud.io/summary/new_code?id=aurelius-kafka-connect-jdbc-sink-base)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-kafka-connect-jdbc-sink-base&metric=reliability_rating&token=a5bcd9f548c5528522d96d7f0296b0336349e65e)](https://sonarcloud.io/summary/new_code?id=aurelius-kafka-connect-jdbc-sink-base)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-kafka-connect-jdbc-sink-base&metric=security_rating&token=a5bcd9f548c5528522d96d7f0296b0336349e65e)](https://sonarcloud.io/summary/new_code?id=aurelius-kafka-connect-jdbc-sink-base)

This Docker image provides a base for all Kafka Connectors that act as a JDBC sink.

## Structure

This Docker image extends the base [`aurelius-kafka-connect-base`](./aurelius-kafka-connect-base.md) image and
provides additional dependencies specifically for JDBC sink connectors.

## Usage

Follow the steps below to use this Docker image as part of a Kafka Connector:

### Dockerfile

Start your `Dockerfile` with the following line:

```dockerfile
FROM aurelius-kafka-connect-jdbc-sink-base:local
```

Next, you can add your worker configurations and any additional dependencies.

??? EXAMPLE "Adding Worker Configurations"

    If your workers are located in a directory named `workers`, you can copy them into the Docker image like this:

    ```dockerfile
    COPY --chown=root:root --chmod=0755 connectors/your-kafka-connect-jdbc-sink-project/workers/*.json /tmp/aurelius/workers/
    ```

### Project Configuration

To ensure that the `aurelius-kafka-connect-jdbc-sink-base` image is built before your Kafka Connector, add the
following line to your `project.json` file:

```json
{
    "implicitDependencies": ["aurelius-kafka-connect-jdbc-sink-base"]
}
```
