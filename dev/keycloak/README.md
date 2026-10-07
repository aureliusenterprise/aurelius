# aurelius-dev-keycloak

Local development Keycloak (identity provider) with a pre-imported realm matching
what the FastAPI backend and Angular frontend expect.

Part of the template **spine**.

## Services

| Service           | Image                         | Host port | Notes                      |
| ----------------- | ----------------------------- | --------- | -------------------------- |
| Keycloak          | `dhi.io/keycloak:26-debian13` | 8080      | `start-dev --import-realm` |
| postgres-keycloak | Postgres (internal)           | —         | Keycloak's own database    |

- Issuer URL: `http://keycloak.localhost:8080` (`KC_HOSTNAME=keycloak.localhost`)
- Realm/client definitions are imported from `import/master.json` on startup —
  edit that file to change realms, clients, or test users
- Telemetry is exported via OTLP to the observability stack (`otel-collector:4317`)

## Running

```bash
nx serve aurelius-dev-keycloak
```

The `serve` target first runs `decrypt` (SOPS) and the project's `docker-build`,
and starts its dependencies (`aurelius-dev-observability`). Keycloak can take a
couple of minutes to become healthy on first start.

> [!NOTE]
> `keycloak.localhost` resolves to 127.0.0.1 on most systems. Log in with the
> credentials defined in `import/master.json` for the admin console.
