# aurelius-atlas-dashboard

The Apache Atlas user interfaces, unchanged ([ADR 046](../../docs/architecture/adr/046-the-catalogue-keeps-its-public-contract.md)):
`dashboardv2` at `/` and `dashboardv3` at `/n/`, built from the Atlas 2.4.0 source tag and served by
nginx, which forwards `/api/` to `aurelius-atlas-server` (DD-001, DD-010).

## Running

```bash
nx docker-build aurelius-atlas-dashboard   # clones Atlas 2.4.0 and builds both dashboards (several minutes)
nx serve aurelius-atlas-server             # the API on :21000, with Elasticsearch
nx serve aurelius-atlas-dashboard          # http://localhost:8081 (classic UI) and /n/ (new UI)
```

Until authentication arrives (increment 6.1) the dashboards load their static pages but stop at the
session call they make first; the admin endpoints already answer.
