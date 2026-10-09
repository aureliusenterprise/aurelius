# aurelius-atlas-dashboard

The Atlas dashboards served unchanged. This file covers wiring specific to this project;
workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `Dockerfile` — stage 1 clones the Atlas tag (commit checked) and runs Atlas's own
  `npm install` + `grunt build-minify` for both dashboards on Node 12.16.0; stage 2 is nginx
- `nginx.conf` — `/` (v2), `/n/` (v3), `/api/` proxied to `aurelius-atlas-server:21000`
- `docker-compose.yaml` — runs the built image against a server on the host
- `e2e/` — Playwright checks of the served pages (Docker)

## Wiring Checklist

- `ATLAS_TAG`/`ATLAS_COMMIT` in the `Dockerfile` must match DD-001 and
  `dev/atlas-reference/reference.sh`.
- The proxy path `/api/` and upstream port must match the server's routes and port.
- Never patch the dashboards' source: they are the contract (ADR 046). A needed change is a
  deviation in `deviations.md`, applied as a documented patch step in the `Dockerfile`.

## Commands

```bash
nx docker-build aurelius-atlas-dashboard
nx serve aurelius-atlas-dashboard
```

## Removal

Part of the spine (ADR 050).
