# aurelius-kafka-connect-jdbc-sink

This Docker image provides a base for all Kafka Connectors that act as a JDBC sink.

## Structure

This Docker image extends the base [`aurelius-kafka-connect`](./aurelius-kafka-connect.md) image and provides
additional dependencies specifically for JDBC sink connectors.

## Usage

Follow the steps below to use this Docker image as part of a Kafka Connector:

### Dockerfile

Start your `Dockerfile` with the following line:

```dockerfile
FROM aurelius-kafka-connect-jdbc-sink:latest
```

Next, you can add your worker configurations and any additional dependencies.

??? EXAMPLE "Adding Worker Configurations"

    If your workers are located in a directory named `workers`, you can copy them into the Docker image like this:

    ```dockerfile
    COPY --chown=root:root --chmod=0755 connectors/your-kafka-connect-jdbc-sink-project/workers/*.json /tmp/aurelius/workers/
    ```

### Project Configuration

To ensure that the `aurelius-kafka-connect-jdbc-sink` image is built before your Kafka Connector, add the following
line to your `project.json` file:

```json
{
    "implicitDependencies": ["aurelius-kafka-connect-jdbc-sink"]
}
```
