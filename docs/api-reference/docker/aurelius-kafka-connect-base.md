# aurelius-kafka-connect-base

This Docker image provides a base for all Kafka Connectors.

## Structure

This Docker image provides some additional dependencies for Kafka Connectors:

- **Startup Scripts**: Included startup scripts make it easier to configure and run Kafka Connectors.
- **Healthchecks**: The image includes healthchecks to ensure that the Kafka Connectors are running correctly.

## Usage

Follow the steps below to use this Docker image as part of a Kafka Connector:

### Dockerfile

Start your `Dockerfile` with the following line:

```dockerfile
FROM aurelius-kafka-connect:latest
```

Next, you can add your worker configurations and any additional dependencies.

??? EXAMPLE "Adding Worker Configurations"

    If your workers are located in a directory named `workers`, you can copy them into the Docker image like this:

    ```dockerfile
    COPY --chown=root:root --chmod=0755 connectors/your-kafka-connect-project/workers/*.json /tmp/aurelius/workers/
    ```

### Project Configuration

To ensure that the `aurelius-kafka-connect-base` image is built before your Kafka Connector, add the following
line to your `project.json` file:

```json
{
    "implicitDependencies": ["aurelius-kafka-connect-base"]
}
```
