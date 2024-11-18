from typing import Any, Dict, List, Union
from confluent_kafka import Consumer, TopicCollection
from confluent_kafka.admin import AdminClient
import json
import io
from avro.io import DatumReader, BinaryDecoder
from avro.schema import parse
from confluent_kafka.schema_registry import SchemaRegistryClient
import random

from m4i_atlas_core.config.config_store import ConfigStore


# Configuration parameters
store = ConfigStore.get_instance()
SCHEMA_REGISTRY_URL = store.get("schema_registry_url")

# Initialize Schema Registry client
if SCHEMA_REGISTRY_URL:
    schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

def get_internal_topic_names(bootstrap_servers: str) -> List[str]:
    """
    Retrieve topic names for the given cluster ID,
    filtering out internal and default topics.
    """
    # Initialize admin client
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    # Get all topics, and then filter for internal topics
    all_topics = [str(t) for t in admin_client.list_topics().topics.values()]
    futureMap = admin_client.describe_topics(TopicCollection(all_topics))
    internal_topics = [topic_name for topic_name, future in futureMap.items() if not (t := future.result()).is_internal]
    return [
        topic
        for topic in internal_topics
        if not topic.endswith(("-offsets", "-status", "-configs"))
    ]


def is_avro(message) -> bool:
    """Check if the message starts with the Avro magic byte (0x00)."""
    return message and message[0] == 0


def deserialize_avro(message):
    """Deserialize an Avro message using the Schema Registry."""
    schema_id = int.from_bytes(message[1:5], byteorder='big')
    avro_schema = schema_registry_client.get_schema(schema_id).schema_str
    schema = parse(avro_schema)
    reader = DatumReader(schema)
    bytes_reader = io.BytesIO(message[5:])  # Skip the magic byte and schema ID
    decoder = BinaryDecoder(bytes_reader)
    return reader.read(decoder)


def consume_messages(topic_names: List[str], bootstrap_servers: str):
    """Consume messages from the provided topic names and parse them."""
    topic_data = []
    for topic in topic_names:
        consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': f'{store.get("consumer_group_id_prefix")}-{random.randint(1, 1000)}',
            'auto.offset.reset': 'earliest'
        })

        consumer.subscribe([topic])
        try:
            msg = consumer.poll(5)

            if msg is None:
                print("No message received")
            elif msg.error():
                print(f"Error while consuming message: {msg.error()}")
            else:
                message_bytes = msg.value()
                value = parse_message(message_bytes, msg.topic())
                if value is not None:
                    topic_data.append({
                        "name": topic,
                        "fields": list(value.keys()),
                    })
        finally:
            consumer.close()
    return topic_data


def parse_message(message_bytes, topic) -> Union[Dict[str, Any], Any]:
    """Attempt to parse the message as JSON or Avro."""
    try:
        value = json.loads(message_bytes.decode('utf-8'))
        print(f"Topic: {topic}, JSON message: {value}")
        return value
    except (UnicodeDecodeError, json.decoder.JSONDecodeError):
        if is_avro(message_bytes):
            try:
                value = deserialize_avro(message_bytes)
                print(f"Topic: {topic}, Avro message: {value}")
                return value
            except Exception as avro_error:
                print(f"Failed to deserialize Avro message: {avro_error}")
        else:
            print(f"Message in topic {topic} is neither JSON nor Avro")
    return None


def discover_cluster() -> List[Dict[str, Any]]:
    """Main function to execute the Kafka topic message consumption process."""
    bootstrap_servers = store.get("bootstrap_servers")
    topic_names = get_internal_topic_names(bootstrap_servers)
    print("Topics:", topic_names)
    topic_data = consume_messages(topic_names, bootstrap_servers)
    print("Topic Data:", topic_data)
    return topic_data
