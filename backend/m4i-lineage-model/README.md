# backend-lineage-model

This application is a backend service that provides an API for generating a lineage graph for a given dataset entity.
It supports the Aurelius Atlas application.

> [!NOTE]
> The application depends on the [backend-data2model](../m4i-data2model/README.md) service to construct the lineage graph.

## Installation

This application is distributed as a Docker image.

> [!IMPORTANT]
> Please make sure you have Docker installed on your machine.
> See the [Docker installation guide](https://docs.docker.com/engine/install/).

To get the latest version of the image, run the following command:

```bash
docker pull ghcr.io/aureliusenterprise/backend-lineage-model:latest
```

Next, you can run the application using the following command:

```bash
docker run -p 7100:7100 ghcr.io/aureliusenterprise/backend-lineage-model:latest
```

The application will be available at `http://localhost:7100`.

## Configuration

The application can be configured using environment variables. The following environment variables are available:

| Environment Variable  | Description                                 | Default Value |
| --------------------- | ------------------------------------------- | ------------- |
| `AUTH_ISSUER`         | The issuer of the JWT token.                | -             |
| `ATLAS_SERVER_URL`    | The URL of the Aurelius Atlas API.          | -             |
| `KEYCLOAK_SERVER_URL` | The URL of the Keycloak server.             | -             |
| `KEYCLOAK_REALM`      | The Keycloak authentication realm.          | -             |
| `KEYCLOAK_CLIENT_ID`  | The Keycloak authentication client ID.      | -             |
| `WSGI_PORT`           | The port on which the application will run. | `7100`        |

## Development

To run the application in development mode, use the following command from the root of the workspace:

```bash
nx serve backend-lineage-model
```

The application will be available at `http://localhost:7100`.
