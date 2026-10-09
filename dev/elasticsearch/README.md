# aurelius-dev-elasticsearch

Local development Elasticsearch 9: the only data store of Aurelius Atlas
([ADR 047](../../docs/architecture/adr/047-one-search-store-is-the-system-of-record.md)).

## Services

| Service       | Image                                                                            | Host port                      |
| ------------- | -------------------------------------------------------------------------------- | ------------------------------ |
| elasticsearch | `docker.elastic.co/elasticsearch/elasticsearch:${ELASTICSEARCH_VERSION}` (9.1.5) | `${ELASTICSEARCH_PORT}` (9200) |

- Single node, security enabled, user `elastic` with the password from `.env` (dev default `changeme`)
- Plain HTTP on the host port; TLS is off in development only (DD-003)
- Attached to the `aurelius-dev-elasticsearch-network` Docker network, which the Atlas server joins

## Running

```bash
nx serve aurelius-dev-elasticsearch   # docker compose up (foreground)
nx up aurelius-dev-elasticsearch      # detached, waits for healthy
curl -u elastic:changeme http://localhost:9200/_cluster/health
```

If Elasticsearch exits at start-up on Linux with a `vm.max_map_count` error, raise it on the Docker host:
`sudo sysctl -w vm.max_map_count=262144`.
