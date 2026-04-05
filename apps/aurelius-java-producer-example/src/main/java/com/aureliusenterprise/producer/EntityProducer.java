package com.aureliusenterprise.producer;

import com.aureliusenterprise.example.Entity;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * EntityProducer is responsible for producing {@link Entity} messages to a Kafka topic.
 * It wraps a {@link KafkaProducer} and provides a method to send entities with a UUID key.
 */
public class EntityProducer {

    /**
     * Logger instance for the producer instance.
     */
    private static final Logger logger = LoggerFactory.getLogger(EntityProducer.class);

    /**
     * KafkaProducer instance used to send {@link Entity} objects with String keys to a Kafka topic.
     */
    private KafkaProducer<String, Entity> producer;

    /**
     * The name of the topic to which entities will be produced.
     */
    private String topicName;

    /**
     * Constructs an {@link EntityProducer} with the specified Kafka producer and topic name.
     *
     * @param producer   the KafkaProducer instance used to send {@link Entity} messages
     * @param topicName  the name of the Kafka topic to which entities will be produced
     */
    public EntityProducer(KafkaProducer<String, Entity> producer, String topicName) {
        this.producer = producer;
        this.topicName = topicName;
    }

    /**
     * Sends an {@link Entity} to the configured topic using the provided UUID key.
     *
     * Converts the UUID key to a string and creates a {@link ProducerRecord} with the key and entity.
     * Throws {@link MissingKeyException} if the key is {@code null}.
     *
     * @param key    the UUID key for the record; must not be {@code null}
     * @param entity the entity to send
     * @throws MissingKeyException if the key is {@code null}
     */
    public void produce(UUID key, Entity entity) {
        if (key == null) {
            throw new MissingKeyException("Key cannot be null");
        }

        String keyString = key.toString();
        ProducerRecord<String, Entity> record = new ProducerRecord<>(this.topicName, keyString, entity);

        this.producer.send(record, this::handleCallback);
    }

    /**
     * Callback handler invoked by Kafka producer after a message send attempt completes.
     * Logs success details including partition and offset, or logs the failure with stack trace.
     *
     * @param metadata   the record metadata containing partition and offset information if successful; may be {@code null} on failure
     * @param exception  the exception thrown during the send operation; {@code null} if the send was successful
     */
    private void handleCallback(RecordMetadata metadata, Exception exception) {
        if (exception != null) {
            EntityProducer.logger.error("Failed to produce message", exception);
        } else {
            EntityProducer.logger.debug(
                "Message produced to partition {} at offset {}",
                metadata.partition(),
                metadata.offset()
            );
        }
    }
}
