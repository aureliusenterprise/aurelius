# backend-consistency-metrics

This application is a backend service that provides an API for calculating various consistency metrics for a given ArchiMate model. It supports the consistency metrics application.

## Installation

This application is distributed as a Docker image.

> [!IMPORTANT]
> Please make sure you have Docker installed on your machine.
> See the [Docker installation guide](https://docs.docker.com/engine/install/).

To get the latest version of the image, run the following command:

```bash
docker pull ghcr.io/aureliusenterprise/backend-consistency-metrics:latest
```

Next, you can run the application using the following command:

```bash
docker run -p 7300:7300 ghcr.io/aureliusenterprise/backend-consistency-metrics:latest
```

The application will be available at `http://localhost:7300`.

## Configuration

The application can be configured using environment variables. The following environment variables are available:

| Environment Variable | Description                                 | Default Value |
| -------------------- | ------------------------------------------- | ------------- |
| `WSGI_PORT`          | The port on which the application will run. | `7300`        |

## Development

To run the application in development mode, use the following command from the root of the workspace:

```bash
nx serve backend-consistency-metrics
```

The application will be available at `http://localhost:7300`.
