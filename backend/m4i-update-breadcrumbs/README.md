# m4i-update-breadcrumbs

CLI tool to update breadcrumbs in Elasticsearch for entities in Aurelius Atlas.

## Description

This tool retrieves breadcrumbs for one or more entities (and optionally their descendants) and updates the breadcrumb information in Elasticsearch, similar to how the synchronize-app-search service handles breadcrumb updates.

## Setup

### Get credentials from Kubernetes

```bash
# Get Elasticsearch password
export ELASTIC_PASSWORD=$(kubectl get secret elastic-search-es-elastic-user -o=jsonpath='{.data.elastic}' -n v2-1-9-alpha-32 | base64 --decode)
```

### Get Atlas access token

You can obtain an Atlas access token using OAuth authentication. The token is used to authenticate with the Atlas API.

```bash
# Example: Get token using the authentication endpoint
export ACCESS_TOKEN=<your-atlas-token>
```

For example, if you're using another Atlas script like `export_atlas.py`:

```bash
python export_atlas.py \
  --token $ACCESS_TOKEN \
  --base-url https://<your-domain>/<namespace>/atlas2/api/atlas \
  --output ../data/export.zip \
  --import-data
```

Replace `<namespace>` with your deployment namespace (e.g., `test-18-11-25`).

## Usage

### Update breadcrumbs for a single entity

```bash
# With access token
python main.py \
  --guid <entity-guid> \
  --atlas-url https://<your-domain>/<namespace>/atlas2/api/atlas \
  --access-token $ACCESS_TOKEN \
  --elastic-url https://<your-domain>/elastic \
  --index app-search-documents \
  --elastic-user elastic \
  --elastic-password $ELASTIC_PASSWORD

# Or with username/password
python main.py \
  --guid <entity-guid> \
  --atlas-url https://<your-domain>/<namespace>/atlas2/api/atlas \
  --atlas-user admin \
  --atlas-password $ATLAS_PASSWORD \
  --elastic-url https://<your-domain>/elastic \
  --index app-search-documents \
  --elastic-user elastic \
  --elastic-password $ELASTIC_PASSWORD
```

### Update breadcrumbs for an entity and all its descendants

```bash
python main.py \
  --guid <entity-guid> \
  --atlas-url https://<your-domain>/<namespace>/atlas2/api/atlas \
  --access-token $ACCESS_TOKEN \
  --elastic-url https://<your-domain>/elastic \
  --index app-search-documents \
  --elastic-user elastic \
  --elastic-password $ELASTIC_PASSWORD \
  --include-descendants
```

### Update breadcrumbs for multiple entities

```bash
python main.py \
  --guid <guid1> \
  --guid <guid2> \
  --atlas-url https://<your-domain>/<namespace>/atlas2/api/atlas \
  --access-token $ACCESS_TOKEN \
  --elastic-url https://<your-domain>/elastic \
  --index app-search-documents \
  --elastic-user elastic \
  --elastic-password $ELASTIC_PASSWORD
```

### Dry run (preview changes without updating)

```bash
python main.py \
  --guid <entity-guid> \
  --atlas-url https://<your-domain>/<namespace>/atlas2/api/atlas \
  --access-token $ACCESS_TOKEN \
  --elastic-url https://<your-domain>/elastic \
  --index app-search-documents \
  --elastic-user elastic \
  --elastic-password $ELASTIC_PASSWORD \
  --dry-run
```

## Parameters

- `--guid`: Entity GUID(s) to update breadcrumbs for (can be specified multiple times)
- `--atlas-url`: Atlas API base URL (e.g., https://<your-domain>/<namespace>/atlas2/api/atlas)
- `--access-token`: Access token for Atlas API authentication
- `--atlas-user`: Atlas username for basic authentication (alternative to access token)
- `--atlas-password`: Atlas password for basic authentication (alternative to access token)
- `--elastic-url`: Elasticsearch URL (e.g., https://<your-domain>/elastic)
- `--index`: Elasticsearch index name (typically `app-search-documents`)
- `--elastic-user`: Elasticsearch username (typically `elastic`)
- `--elastic-password`: Elasticsearch password
- `--elastic-api-key`: Elasticsearch API key (alternative to username/password)
- `--include-descendants`: Include all descendants of the specified entities
- `--choose-first-parent`: When an entity has multiple parents, choose the first one (default: raises error)
- `--dry-run`: Preview changes without writing to Elasticsearch
- `--verbose`: Enable verbose logging (DEBUG level)
