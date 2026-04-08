# aurelius-frontend-example

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-frontend-example&metric=sqale_rating&token=81cdfca44977faa29718f4be1d46a9efa05efda0)](https://sonarcloud.io/summary/new_code?id=aurelius-frontend-example)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-frontend-example&metric=reliability_rating&token=81cdfca44977faa29718f4be1d46a9efa05efda0)](https://sonarcloud.io/summary/new_code?id=aurelius-frontend-example)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-frontend-example&metric=security_rating&token=81cdfca44977faa29718f4be1d46a9efa05efda0)](https://sonarcloud.io/summary/new_code?id=aurelius-frontend-example)

This is an example frontend application built with Angular.

## Deployment

Deploy using the provided Dockerfile. By default, the app listens on [http://localhost:8080](http://localhost:8080).

## Configuration

The following environment variables can be used to configure the application:

| Name                   | Description                     | Required | Default Value |
| ---------------------- | ------------------------------- | -------- | ------------- |
| `AURELIUS_BACKEND_URL` | The URL of the backend API.     | Yes      | N/A           |
| `KEYCLOAK_CLIENT_ID`   | The Keycloak client ID.         | Yes      | N/A           |
| `KEYCLOAK_REALM`       | The Keycloak realm.             | Yes      | N/A           |
| `KEYCLOAK_URL`         | The URL of the Keycloak server. | Yes      | N/A           |

### Nginx Configuration

The application uses Nginx as a reverse proxy to forward API requests to the Aurelius backend. The Nginx configuration
is located in `nginx.conf`. By default, it forwards requests from `/api` to the URL specified in the `AURELIUS_BACKEND_URL`
environment variable. You can modify this configuration if your backend API is located at a different path or
if you want to add additional proxy rules.
