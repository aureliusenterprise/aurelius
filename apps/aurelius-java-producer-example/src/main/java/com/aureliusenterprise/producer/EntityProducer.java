package com.aureliusenterprise.producer;

import com.aureliusenterprise.example.Entity;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

public class EntityProducer {

    private KafkaProducer<String, Entity> producer;
    private String topicName;

    public EntityProducer(KafkaProducer<String, Entity> producer, String topicName) {
        this.producer = producer;
        this.topicName = topicName;
    }

    public void produce(UUID key, Entity entity) {
        if (key == null) {
            throw new MissingKeyException("Key cannot be null");
        }

        String keyString = key.toString();
        ProducerRecord<String, Entity> record = new ProducerRecord<>(this.topicName, keyString, entity);

        this.producer.send(record);
    }
}
