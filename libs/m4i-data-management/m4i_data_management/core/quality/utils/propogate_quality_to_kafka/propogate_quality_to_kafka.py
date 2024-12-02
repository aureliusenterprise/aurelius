import logging

from m4i_atlas_core.config.config_store import ConfigStore
from .... import make_confluent_producer
import pandas as pd
from pandas import DataFrame, notnull

log = logging.getLogger(__name__)
store = ConfigStore.get_instance()


def write_data_quality_results_to_kafka(results: DataFrame, compliant: DataFrame, non_compliant: DataFrame):
    """
    write data quality results to kafka
    :param results: the data quality results
    :param compliant: The compliant fields to the data quality rules
    :param non_compliant: The non-compliant fields to the data quality rules
    :return: writes the results to kafka_quality_summary_topic defined in the config.
        writes the compliant and non_compliant, with the removal of data to kafka_quality_detail_topic
        defined in config.


    Expected in config:
        "kafka_quality_summary_topic" |string | required
        "kafka_quality_detail_topic" |string | required
        "dataset_index_column" |string  | required
        'sasl_flag' | Bool | optional | default True
        "confluent.kafka.bootstrap.servers" |string | required
    if sasl_flag:
        "confluent.auth.sasl.username" |string | required
        "confluent.auth.sasl.password" |string | required

    """

    results = results.set_index(keys=['business_rule_id'], drop=False)
    results = results.where(notnull(results), None)
    results['result_id'] = results["result_id"].map(str)
    results['run_id'] = results["run_id"].map(str)

    kafka_summary_topic_name, kafka_details_topic_name, dataset_index_column = store.get_many(
        "kafka_quality_summary_topic",
        "kafka_quality_detail_topic",
        "dataset_index_column",
        all_required=True
    )
    producer = make_confluent_producer()

    for id, row in results.iterrows():
        row_data = row.to_dict()
        producer.produce(topic=kafka_summary_topic_name, value=row_data)

    columns = [dataset_index_column] + [
                  'business_rule_id', 'data_field_qualified_name', 'data_quality_rule_description',
                  'data_quality_rule_dimension', 'result_id', 'test_date', 'run_id', 'run_date',
                  'data_attribute_qualified_name', 'data_field_name', 'data_entity_qualified_name',
                  'data_attribute_name', 'data_attribute_owner', 'data_attribute_steward',
                  'data_domain_qualified_name', 'data_entity_name', 'data_domain_name'
              ]

    compliant = compliant[columns]
    compliant = compliant.assign(passed=1)

    non_compliant = non_compliant[columns]
    non_compliant = non_compliant.assign(passed=0)

    details = pd.concat([compliant, non_compliant])

    details['data_index_rule_id'] = details[dataset_index_column].astype(
        str) + '--' + details['business_rule_id'].astype(str)
    details = details.set_index('data_index_rule_id')
    details = details.where(notnull(details), None)
    details['result_id'] = details["result_id"].map(str)
    details['run_id'] = details["run_id"].map(str)

    for id, row in details.iterrows():
        row_data = row.to_dict()
        producer.produce(topic=kafka_details_topic_name, value=row_data)
    producer.flush()

# END write_data_quality_results_to_kafka
