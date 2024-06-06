# backend-data2model

This application is a backend service that provides an API for converting a given dataset to an ArchiMate model. It supports the data2model application.

## Installation

This application is distributed as a Docker image.

> [!IMPORTANT]
> Please make sure you have Docker installed on your machine.
> See the [Docker installation guide](https://docs.docker.com/engine/install/).

To get the latest version of the image, run the following command:

```bash
docker pull ghcr.io/aureliusenterprise/backend-data2model:latest
```

Next, you can run the application using the following command:

```bash
docker run -p 7000:7000 ghcr.io/aureliusenterprise/backend-data2model:latest
```

The application will be available at `http://localhost:7000`.

## Configuration

The application can be configured using environment variables. The following environment variables are available:

| Environment Variable | Description                                 | Default Value |
| -------------------- | ------------------------------------------- | ------------- |
| `AUTH_ISSUER`        | The issuer of the JWT token.                | -             |
| `WSGI_PORT`          | The port on which the application will run. | `7000`        |

## Development

To run the application in development mode, use the following command from the root of the workspace:

```bash
nx serve backend-data2model
```

The application will be available at `http://localhost:7000`.
