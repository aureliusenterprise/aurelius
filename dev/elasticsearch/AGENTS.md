# aurelius-dev-elasticsearch

Local development Elasticsearch. This file covers wiring specific to this project;
workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `docker-compose.yaml` — single Elasticsearch 9 node
- `.env` / `.env.enc` — SOPS-encrypted dev settings (version, port, password, heap)

## Wiring Checklist

- Exposes the Docker network `aurelius-dev-elasticsearch-network`; the Atlas server
  attaches to it (from increment 0.5).
- `ELASTICSEARCH_VERSION` must match the image used by the component tests in
  `libs/python/aurelius-atlas-store-es` (`aurelius_atlas_store_es.testing.DEFAULT_IMAGE`)
  and the version in `dev/atlas-reference` is unrelated (that one is Atlas's own store).
- Credentials are the same dev defaults the Atlas server's settings model reads.

## Commands

```bash
nx serve aurelius-dev-elasticsearch   # compose up (foreground)
nx up aurelius-dev-elasticsearch      # detached, waits for healthy
```

## Conventions

- Keep it an empty cluster: indices, mappings and templates belong to the
  application (`aurelius-atlas-store-es`), never to compose init scripts.
- Development settings that weaken security (`*.ssl.enabled: false`, disk threshold
  off) are recorded in DD-003 and must never be copied to a deployment.

## Removal

Part of the spine ([ADR 047](../../docs/architecture/adr/047-one-search-store-is-the-system-of-record.md)).
Removing it means replacing the store of the whole system.
