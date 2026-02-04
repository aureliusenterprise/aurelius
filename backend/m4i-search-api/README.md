# backend-search-api

A lightweight Flask service that proxies Elastic/App Search calls and enforces Atlas user authentication. Clients call this API with their Atlas bearer token; the service forwards the request to Elastic using a static App Search token so the frontend never needs to know it.

## Endpoints

- `/*` – any path is forwarded verbatim to `APP_SEARCH_BASE_URL + /<path>` using the same HTTP method.
- `GET /heartbeat` – health check (from `m4i-backend-core`).

Requests are passed through with `Authorization: Bearer <APP_SEARCH_TOKEN>`. Payload, query params, and `X-Request-ID` / `X-Correlation-ID` headers are forwarded when present.

## Configuration

| Variable | Description | Example |
| --- | --- | --- |
| `APP_SEARCH_BASE_URL` | Base URL of the Elastic/App Search instance (no trailing slash). | `https://elastic.example.com/api/as/v1/engines/atlas-dev/search.json` |
| `APP_SEARCH_TOKEN` | Static App Search API token used by this service. | `search-xxxx` |
| `APP_SEARCH_TIMEOUT_SECONDS` | Request timeout when calling App Search (default `15`). | `20` |
| `APP_SEARCH_VERIFY_SSL` | Whether to verify TLS certs when calling App Search (default `true`). | `false` |
| `AUTH_ISSUER` | Expected issuer for Atlas JWT validation. | `https://auth.example.com/realms/atlas` |
| `AUTH_PUBLIC_KEY` | RSA public key used to validate Atlas JWTs. | `-----BEGIN PUBLIC KEY-----...` |
| `WSGI_PORT` | Gunicorn listen port (used in serve/Docker). | `6970` |

## Development

Run locally from the workspace root:

```bash
nx serve backend-search-api
```

The service listens on `http://127.0.0.1:${WSGI_PORT}` (default `6970`).

## Docker

Build and run the container image:

```bash
nx run backend-search-api:docker-build --version latest
nx run backend-search-api:docker-publish --version latest
```

## Notes

- Authentication uses `m4i-backend-core` so the same Atlas user JWT required by other backend services works here.
- The service forwards the Elastic response body and status code unchanged.
