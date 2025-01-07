from confluent_kafka import Producer

from m4i_atlas_core import ConfigStore

config = ConfigStore.get_instance()


def make_confluent_producer() -> Producer:
    """
    Returns a connection to Confluent Kafka in the Data Management Platform that can be used to push change events.

    It is assumed that sasl is used, if this is not the case please set the in the config key "sasl_flag" to False
    """
    sasl_flag = config.get('sasl_flag', default=True)
    bootstrap_server_url = config.get("confluent.kafka.bootstrap.servers", required=True)

    if sasl_flag:
        username, password = config.get_many(
            "confluent.auth.sasl.username",
            "confluent.auth.sasl.password",
            all_required=True
        )

        producer_config = {
            "bootstrap.servers": bootstrap_server_url,
            "sasl.mechanisms": "PLAIN",
            "sasl.password": password,
            "sasl.username": username,
            "security.protocol": "SASL_SSL"
        }
    else:
        producer_config = {
            "bootstrap.servers": bootstrap_server_url,
        }

    return Producer(**producer_config)
# END make_confluent_producer
