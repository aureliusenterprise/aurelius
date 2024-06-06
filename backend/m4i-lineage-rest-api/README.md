# backend-lineage-rest-api

This application is a backend service that provides an API for registering applications and data flows in the Aurelius Atlas application. It is intended to be used by deployment pipelines to register the lineage of the deployed applications.

## Installation

This application is distributed as a Docker image.

> [!IMPORTANT]
> Please make sure you have Docker installed on your machine.
> See the [Docker installation guide](https://docs.docker.com/engine/install/).

To get the latest version of the image, run the following command:

```bash
docker pull ghcr.io/aureliusenterprise/backend-lineage-rest-api:latest
```

Next, you can run the application using the following command:

```bash
docker run -p 6969:6969 ghcr.io/aureliusenterprise/backend-lineage-rest-api:latest
```

The application will be available at `http://localhost:6969`.

## Configuration

The application can be configured using environment variables. The following environment variables are available:

| Environment Variable  | Description                                 | Default Value |
| --------------------- | ------------------------------------------- | ------------- |
| `AUTH_ISSUER`         | The issuer of the JWT token.                | -             |
| `ATLAS_SERVER_URL`    | The URL of the Aurelius Atlas API.          | -             |
| `KEYCLOAK_SERVER_URL` | The URL of the Keycloak server.             | -             |
| `KEYCLOAK_REALM`      | The Keycloak authentication realm.          | -             |
| `KEYCLOAK_CLIENT_ID`  | The Keycloak authentication client ID.      | -             |
| `WSGI_PORT`           | The port on which the application will run. | `6969`        |

## Development

To run the application in development mode, use the following command from the root of the workspace:

```bash
nx serve backend-lineage-rest-api
```

The application will be available at `http://localhost:6969`.
