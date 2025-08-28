from typing import List, Union

from confluent_kafka import TopicCollection
from confluent_kafka.admin import AdminClient


def get_cluster_id(admin_client: AdminClient) -> Union[str, None]:
    """Retrieve the cluster ID from the Kafka admin client."""
    future = admin_client.describe_cluster()

    return (
        cluster_metadata.cluster_id if (cluster_metadata := future.result()) else None
    )


def get_external_topic_names(admin_client: AdminClient) -> List[str]:
    """Retrieve topic names for the given cluster ID, filtering out internal and default topics."""
    all_topics = [str(t) for t in admin_client.list_topics().topics.values()]

    futures = admin_client.describe_topics(TopicCollection(all_topics))

    external_topics = [
        topic_name
        for topic_name, future in futures.items()
        if not ((t := future.result()) and t.is_internal)
    ]

    return [
        topic
        for topic in external_topics
        if not topic.startswith("_")
        or topic.endswith(("-offsets", "-status", "-configs"))
    ]
