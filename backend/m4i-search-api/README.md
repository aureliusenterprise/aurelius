# m4i-search-api

A lightweight Flask service that proxies Elastic/App Search calls and enforces Atlas user authentication. Clients
call this API with their Atlas bearer token; the service forwards the request to Elastic using server-side credentials
to fetch an App Search private key, so the frontend never needs to know it.

## Endpoints

- `POST /api/as/v1/engines/<engine>/search`
- `POST /api/as/v1/engines/<engine>/search.json`
- Any other App Search route or method is denied with `403`.
- `GET /health` – health check.

Requests are authenticated with an Atlas JWT. The service fetches an App Search private key using
`APP_SEARCH_USERNAME`/`APP_SEARCH_PASSWORD` and forwards requests with that key. Payload, query parameters, and
end-to-end headers are forwarded for allowlisted routes only.

## Configuration

| Variable                     | Description                                                                          | Example                                 |
| ---------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------- |
| `APP_SEARCH_BASE_URL`        | Base URL of the Enterprise Search instance (no trailing slash).                      | `https://elastic.example.com`           |
| `APP_SEARCH_USERNAME`        | Username for fetching the App Search private key.                                    | `elastic`                               |
| `APP_SEARCH_PASSWORD`        | Password for fetching the App Search private key.                                    | `***`                                   |
| `APP_SEARCH_TIMEOUT_SECONDS` | Request timeout in seconds (default `15`).                                           | `20`                                    |
| `APP_SEARCH_CA_CERT_PATH`    | Path to CA certificate for SSL verification. If unset, SSL verification is disabled. | `/etc/ssl/certs/ca-cert.pem`            |
| `AUTH_ISSUER`                | Issuer URL for JWKS-based JWT validation.                                            | `https://auth.example.com/realms/atlas` |
| `WSGI_PORT`                  | Gunicorn listen port.                                                                | `6970`                                  |

## Development

Run locally from the workspace root:

```bash
nx serve m4i-search-api
```

The service listens on `http://127.0.0.1:${WSGI_PORT}` (default `6970`).

## Docker

Build and run the container image:

```bash
nx run m4i-search-api:docker-build --version latest
nx run m4i-search-api:docker-publish --version latest
```
