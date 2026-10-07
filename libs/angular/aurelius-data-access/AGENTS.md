# aurelius-data-access

Typed Angular data layer for the FastAPI example backend. This file covers wiring
specific to this lib; workspace-wide rules live in the root `AGENTS.md` and the
Angular lib recipe in `libs/angular/AGENTS.md`.

## Layout

- `src/lib/entities/` — `EntitiesService` (HTTP + SSE) and the API types;
  `src/index.ts` is the public API
- `.spec.ts` files colocated with source

## Wiring Checklist

- `tsconfig.base.json` — `aurelius-data-access` path alias used by the frontend.
- The backend contract: endpoints (`/entities/*`, `/entities/sse`), `Envelope<T>`,
  and `PaginatedResponse<T>` must match `apps/aurelius-fastapi-example`.
- `Entity` mirrors `libs/python/aurelius-example` **by hand** — when the Python
  model changes, update this type too (see that lib's AGENTS.md for the full
  ripple list).
- `package.json` — peer deps (`ngx-sse-client`, Angular) keep the stale `^21`
  version; update when touching this file.

## Commands

```bash
nx test aurelius-data-access -c ci   # Vitest unit tests
nx build aurelius-data-access        # ng-packagr-lite package build
```

## Conventions

- Every backend endpoint gets a typed method here — components never call
  `HttpClient` directly.
- New response shapes go in the types file next to `Entity`, exported from
  `src/index.ts`.
- SSE stays on `ngx-sse-client` with cleanup on destroy; don't hand-roll
  `EventSource`.

## Removal

Part of the spine. Removing it means removing the `aurelius-data-access` alias and
all imports in `aurelius-frontend-example` (its components would need their own
HTTP calls), plus its `mkdocs.yaml` entries.
