from confluent_kafka import Consumer
from m4i_atlas_core.config.config_store import ConfigStore

config = ConfigStore.get_instance()


def make_confluent_consumer(enable_auto_commit: bool = True) -> Consumer:

    bootstrap_server_url, group_id, username, password = config.get_many(
        "confluent.kafka.bootstrap.servers",
        "confluent.kafka.group.id",
        "confluent.auth.sasl.username",
        "confluent.auth.sasl.password"
    )

    consumer_config = {
        "auto.offset.reset": "earliest",
        "bootstrap.servers": bootstrap_server_url,
        "enable.auto.commit": enable_auto_commit,
        "group.id": group_id,
        "sasl.mechanisms": "PLAIN",
        "sasl.password": password,
        "sasl.username": username,
        "security.protocol": "SASL_SSL"
    }

    return Consumer(consumer_config)
# END make_confluent_consumer
