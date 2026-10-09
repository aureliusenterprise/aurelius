# aurelius-dev-atlas-reference

The reference implementation for parity testing
([ADR 048](../../docs/architecture/adr/048-behaviour-is-proven-against-the-reference-before-it-is-accepted.md)):
Apache Atlas 2.4.0, built from its source tag with Atlas's own Docker set-up
(`dev-support/atlas-docker`), with HBase, Solr, ZooKeeper, Kafka and HDFS in containers.

It is needed only to **record** parity fixtures. Everyday test runs and CI compare against the recorded
fixtures and never start it.

## Running

Needs Docker with at least 6 GB of memory and about 15 GB of disk.

```bash
nx build-atlas aurelius-dev-atlas-reference   # once: clone, download archives, build (up to an hour)
nx up aurelius-dev-atlas-reference            # start; waits until http://localhost:21000 answers
nx down aurelius-dev-atlas-reference          # stop
```

The UI and API are at <http://localhost:21000>, user `admin`, password `atlasR0cks!` (Atlas's
development default).

## Recording fixtures

With the reference running, record the parity scenarios (see
`libs/python/aurelius-atlas-parity/README.md`):

```bash
nx record-parity aurelius-atlas-server
```
