# atlas-post-install
Container image for automating post-installation steps in Aurelius Atlas.

## Environment variables
To configure the job you have to specify the following environment variables:

| variable | description | required |
| - | - | - |
| NAMESPACE | Kubernetes release namespace | no |
| ELASTIC_URL | base url of the elastic cluster | yes |
| ENTERPRISE_SEARCH_URL | base url of the enterprise search | yes |
| ELASTIC_USERNAME | elastic username for authentication | no (default: `elastic`) |
| ELASTIC_PASSWORD | elastic password for authentication | yes |
| ELASTIC_CERTIFICATE_PATH | elastic certificate path for authentication | no |

Additionally, all the variables mentioned in [flink-ci README](https://github.com/aureliusenterprise/flink-ci/blob/f/separate_jobs/README.md#configuration).
