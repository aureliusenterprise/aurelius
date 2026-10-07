# aurelius-data-access

Typed Angular data layer for the Aurelius example backend: an HTTP + SSE client
service and the TypeScript types mirroring the API contract.

Part of the template **spine**.

## API

- `EntitiesService` — CRUD and search against the FastAPI example
  (`/entities/*`), plus `GET /entities/sse` live updates via
  `ngx-sse-client` (auto-reconnecting, cleaned up on destroy)
- `Entity` — the domain type mirroring `libs/python/aurelius-example`
- `Envelope<T>`, `PaginatedResponse<T>`, `FindAllQueryParams` — API response and
  query shapes

## Usage

```ts
import { EntitiesService, type Entity } from "aurelius-data-access";

private readonly entities = inject(EntitiesService);
```

> [!NOTE]
> `Entity` here and the Python `Entity` model are kept in sync by hand — update
> both when the domain model changes.

## Testing

```bash
nx test aurelius-data-access -c ci   # Vitest unit tests
```
