# aurelius-atlas-server

The Apache Atlas 2.4.0 REST API, implemented in Python on Elasticsearch 9
([ADR 046](../../docs/architecture/adr/046-the-catalogue-keeps-its-public-contract.md),
[ADR 047](../../docs/architecture/adr/047-one-search-store-is-the-system-of-record.md)).
Which endpoints exist is tracked per increment in the
[roadmap](../../docs/architecture/conversion/index.md#roadmap).

## Endpoints so far

| Endpoint                         | Increment | Notes                                        |
| -------------------------------- | --------- | -------------------------------------------- |
| `GET /api/atlas/admin/version`   | 0.5       | `Revision` is this build's commit (DV-03)    |
| `GET /api/atlas/admin/status`    | 0.5       | Always `ACTIVE` (no passive mode)            |
| `GET /api/atlas/admin/liveness`  | 0.5       |                                              |
| `GET /api/atlas/admin/readiness` | 0.5       | Ready while Elasticsearch is green or yellow |

No authentication yet (increment 6.1): do not expose this server outside a development machine.

## Running

```bash
nx serve aurelius-atlas-server          # starts Elasticsearch, then the API on http://localhost:21000
nx test aurelius-atlas-server -c ci     # unit tests, plus parity tests (Docker)
nx record-parity aurelius-atlas-server  # record fixtures from the reference Atlas (nx up aurelius-dev-atlas-reference)
```

Settings come from `AURELIUS_ATLAS_SERVER_*` environment variables (or `.env`), see
`aurelius_atlas_server/settings.py`.
