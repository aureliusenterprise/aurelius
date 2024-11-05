# m4i_data_dictionary_io

This application allows for reading Data Dictionary Excels and pushing the defined entities in bulk
to Aurelius Atlas. Data Dictionary is expected to be in the same format as the template Data Dictionary.

## How to run

To run the application, please follow the steps below:

### Production

To run the application in the production environment, please run the following command:

```bash
python -m m4i_data_dictionary_io
```

### Development

To run the application in the development environment, please run the following command:

```bash
nx serve m4i-data-dictionary-io
```

## Configuration

The following environment variables can be set to configure the behavior of the app:

| Name | Required | Description |
|---|---|---|
| `ATLAS_CREDENTIALS_USERNAME` | True |  The Username to be used to access the Atlas Instance. |
| `ATLAS_CREDENTIALS_PASSWORD` | True | The Password to be used to access the Atlas Instance must correspond to the Username given. |
| `ATLAS_SERVER_URL` | True |  The Server Url that Atlas runs on, with '/api/atlas' post fix. |
| `DATA_DICTIONARY_PATH` | True |  The Path to the Data Dictionary to be loaded.|
| `VALIDATE_QUALIFIED_NAME` | False | If to validate the qualified Names given. This is default to True, however, if the entities provided in the data dictionary do not follow the qualified Name schema, the validation can be turned off by setting this configuration to False. |
| `SOURCE` | True | The source from which we read the metadata. Options are: `excel`, `kafka` |
| `SCHEMA_REGISTRY_URL` | False | The URL of the schema registry. Used when reading metadata from Kafka to manage schemas. |
| `BOOTSTRAP_SERVERS` | False False | The Kafka bootstrap servers to connect to, formatted as a comma-separated list of host |
| `CONSUMER_GROUP_ID_PREFIX`| False | A prefix for the consumer group ID used when reading from Kafka, allowing logical grouping of consumers. |

## Testing

This project uses `pytest` as its unit testing framework. To run the unit tests, please run the following command:

```bash
nx test m4i-data-dictionary-io
```
