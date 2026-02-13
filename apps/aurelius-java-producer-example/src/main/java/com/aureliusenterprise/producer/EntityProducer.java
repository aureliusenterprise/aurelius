package com.aureliusenterprise.producer;

import com.aureliusenterprise.example.Entity;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

/**
 * EntityProducer is responsible for producing {@link Entity} messages to a Kafka topic.
 * It wraps a {@link KafkaProducer} and provides a method to send entities with a UUID key.
 */
public class EntityProducer {

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

        this.producer.send(record);
    }
}
