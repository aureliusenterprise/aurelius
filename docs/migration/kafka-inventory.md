# Kafka inventory (pyatlas migration, phase 0)

With the big-bang cutover Kafka, Zookeeper, Kafka Connect and Kafka UI are switched off. This is every Kafka
producer and consumer found in the monorepo (main, commit 13ea6015) and what replaces it. Decided 28 Sep 2026:
all of them are removed without replacement on Kafka; nothing outside this repository is kept connected.

| Topic | Producer | Consumer | After the migration |
| --- | --- | --- | --- |
| `ATLAS_HOOK` | Atlas hooks of other systems (none in this repo) | Apache Atlas | Removed. Systems that want to write metadata use the pyatlas REST API. |
| `ATLAS_ENTITIES` | Apache Atlas (entity notifications) | the three Flink jobs (`kafkaSourceTopicName`) | Removed; pyatlas in-process change events. |
| `publish-state` | Flink `m4i-publish-state` | Kafka Connect `publish_state.json` → ES index; read back by the other Flink jobs (previous entity version) | Not needed: change events carry the old and new entity. |
| `.ent-search-engine-documents-atlas-dev` | Flink `m4i-synchronize-app-search` | Kafka Connect `app_search_documents.json` → the ES index behind App Search engine `atlas-dev` | pyatlas search-documents module writes the index itself. |
| `.ent-search-engine-documents-atlas-dev-gov-quality` | Flink `m4i-update-gov-data-quality` | Kafka Connect `gov_data_quality_documents.json` → engine `atlas-dev-gov-quality` | pyatlas quality module. |
| `DEAD_LETTER_BOX` | the three Flink jobs (failed messages) | people, via Kafka UI | pyatlas outbox failures, logs and metrics. |
| `kafka_quality_summary_topic`, `kafka_quality_detail_topic` (names from config) | `m4i-data-management` `propogate_quality_to_kafka` (library function; no caller in this repo) | unknown | Removed (with the library function in phase 6); data quality results go to the pyatlas data-quality ingestion API (phase 3). |
| customer topics + schema registry | customer systems | `apps/m4i-data-dictionary-io` Kafka source | Switched off (decision 28 Sep 2026); the data dictionary is imported from Excel only. |
| Kafka Connect storage topics | Kafka Connect | Kafka Connect | Gone with Kafka Connect. |

Other Kafka references that go away with the cutover:

- `k8s/charts/{kafka,kafka-connect,kafka-ui,zookeeper,flink-*}` and their reverse-proxy routes
  (`conf.d/kafka-connect.yaml`, `conf.d/kafka-ui.yaml`, `conf.d/flink.yaml`).
- The Kafka UI card of `apps/index-page` (`components/cards/kafka-ui`).
- `atlas.kafka.*` / `atlas.notification.*` in `k8s/charts/atlas/conf/atlas-application--properties.yaml` (the
  whole Atlas chart goes).

Not affected: the m4i lineage types `m4i_kafka_topic`, `m4i_kafka_cluster`, ... describe Kafka in a customer's
landscape; they stay (`backend/pyatlas/models/9000-Aurelius/9040-m4i_connectors_model.json`).

Data quality results (`atlas-dev-quality` engine) have no Kafka Connect worker; today they are uploaded through
the App Search API (post-install `upload_documents`, `propagate_quality.py`). Decided: they are written through
the pyatlas data-quality ingestion API (phase 3).
