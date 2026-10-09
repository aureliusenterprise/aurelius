# aurelius-atlas-store-es

Access to Elasticsearch 9, the only store of Aurelius Atlas
([ADR 047](../../../docs/architecture/adr/047-one-search-store-is-the-system-of-record.md)).

Today it provides the foundation every later store module builds on:

| Module                             | What it does                                                                  |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `aurelius_atlas_store_es.settings` | `ElasticsearchSettings`: hosts, credentials, index prefix, timeouts           |
| `aurelius_atlas_store_es.client`   | `create_client`, `check_health`, `ClusterHealth`, `StoreUnavailableError`     |
| `aurelius_atlas_store_es.indices`  | `index_name`: the `<prefix>-<kind>` naming rule (DD-004)                      |
| `aurelius_atlas_store_es.testing`  | `elasticsearch_node`: a disposable node for component tests (extra `testing`) |

```python
from aurelius_atlas_store_es.client import check_health, create_client
from aurelius_atlas_store_es.settings import ElasticsearchSettings

settings = ElasticsearchSettings(password="changeme")
client = create_client(settings)
health = await check_health(client)
await client.close()
```

Index layouts for typedefs, entities and relationships arrive with increments 1.3, 2.2 and 3.1.
