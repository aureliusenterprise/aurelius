# Data Quality on DMP Governance - Atlas
Is used to determine the quality of various entities already loaded into DMP's governance tool - Apache Atlas. 
It verifies data loaded against various m4i types ( like m4i_data_domain, m4i_data_entity ) on quality measures like completeness, uniqueness etc.

There are two main categories of Data that is generated for each m4i Type entity. 
 
   * Attributes related data
     consists of details about entity attributes where certain quality metrics can be applied like 
       * completeness -- whether we have a value for an attribute
       * uniqueness -- whether values are unique for different entities
       
   * Relationships related data
     consists of details about entity relationships where certain quality metrics can be applied like
       * completeness -- whether we have correct relationships between two entities.

# Configuring Rules
An important aspect of Data Quality is the rules that are applied to each entity. 
There are separate rules for attributes and relationships. However, the structure is same and follows as below.

```yaml
  id: id
  expressionVersion: version of expression
  expression: expression to evaluate `completeness('name')`
  qualifiedName: unique name for the rule example:`m4i_data_domain--name`
  qualityDimension: Rule Category - explained below
  ruleDescription: Description of the rule ex:`name is not None and is not empty`
  compliantMessage: This entity has a name
  noncompliantMessage: This entity is missing a name
  active: 0 | 1 
  type: attribute | relationship
```

| Rule Category | Rule Description | 
|---|---|
| _completeness_ | degree to which data is not null |
| _accuracy_ | degree to which a column conforms to a standard |
| _validity_ | degree to which the data comply with a predefined structure |
| _uniqueness_ | degree to which the data has a unique value | 
| _timeliness_ | the data should be up to date |

Example
```yaml
    id: 1
    expressionVersion: 1
    expression: completeness('name')
    qualifiedName: m4i_data_domain--name
    qualityDimension: completeness
    ruleDescription: name is not None and is not empty
    compliantMessage: This entity has a name
    noncompliantMessage: This entity is missing a name
    active: 1
    type: attribute
```
`Rules` are maintained in `rules` directory of the package and can be found for each m4i type.

# Running the code
We can execute `run.py` file. This will generates 6 files in output folder of the package. Three each for attributes 
and relationships. In addition, generated data is pushed to Elasticsearch indexes. We can configure pre-fix of indexes by updating
`elastic_index_prefix` for both attributes and relationships related data.

* Summary -- gives a summary of the data quality results.
* Complaint Data -- gives information about complaints.
* Non-complaint Data -- gives information about non-complaints.

## Configurations and Credentials
Please make a copy of `config.sample.py` and `credentials.sample.py` and rename the files to `config.py` and `credentials.py` respectively.
Please set the configuration parameters and credentials for `atlas` and `elastic` as below.

`credentials.py`
Should contain two dictionaries viz `credential_atlas` and `credential_elastic`

| Name | Description | 
|---|---|
| credential_atlas[atlas.credentials.username] |  The Username to be used to access the Atlas Instance. | 
| credential_atlas[atlas.credentials.password] | The Password to be used to access the Atlas Instance must correspond to the Username given. | 
| credential_elastic[elastic_cloud_id] |  Service URL for Elastic. | 
| credential_elastic[elastic_cloud_username] |  The Username to be used to access the Elastic Instance. | 
| credential_elastic[elastic_cloud_password] | The Password to be used to access the Elastic Instance must correspond to the Username given. | 

`config.py`
Should contain two dictionaries viz `config_elastic` and `config_atlas`

| Name | Description | 
|---|---|
| config_elastic[elastic_index_prefix] | Define prefix for the elastic Index where data will be pushed to|
| config_atlas[atlas.server.url] |  The Server URL that Atlas runs on, with `/api/atlas` post fix. |
| config_atlas[atlas.credentials.token] |  Add Keycloak access token |

#Structure

```
├───nxtgen_governance_data_quality
│   │   __init__.py
│   │
│   ├───core
│   │   │   __init__.py
│   │   │
│   │   ├───parse_entity
│   │   │   │   ParseEntity.py
│   │   │   │   __init__.py
│   │   │
│   │   ├───read_type
│   │   │   │   ReadType.py
│   │   │   │   __init__.py
│   │   │
│   │   ├───rules
│   │   │   │   Rules.py
│   │   │   │   __init__.py
├───output
├───rules
│       m4i_collection.yaml
│       m4i_confluent_environment.yaml
│       m4i_dashboard.yaml
│       m4i_dataset.yaml
│       m4i_data_attribute.yaml
│       m4i_data_domain.yaml
│       m4i_data_entity.yaml
│       m4i_elastic_cluster.yaml
│       m4i_elastic_field.yaml
│       m4i_elastic_index.yaml
│       m4i_field.yaml
│       m4i_kafka_cluster.yaml
│       m4i_kafka_field.yaml
│       m4i_kafka_topic.yaml
│       m4i_person.yaml
│       m4i_system.yaml
│       m4i_visualization.yaml
│
├───scripts
│       run.py
```

# Updates
Data needed to be added to App search and entities are created in dev atlas. new function `_push_rules_to_atlas` in `Rules` class was added,
This function creates the entities in atlas.
