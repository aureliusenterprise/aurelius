package com.aureliusenterprise.producer;

import com.aureliusenterprise.example.Entity;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import java.util.Properties;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger logger = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        Properties props = new Properties();

        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);

        try {
            props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, System.getenv("KAFKA_BOOTSTRAP_SERVERS"));
        } catch (NullPointerException e) {
            App.logger.error("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.");
            System.exit(1);
        }

        try {
            props.put("schema.registry.url", System.getenv("SCHEMA_REGISTRY_URL"));
        } catch (NullPointerException e) {
            App.logger.error("SCHEMA_REGISTRY_URL environment variable is not set.");
            System.exit(1);
        }

        KafkaProducer<String, Entity> kafkaProducer = new KafkaProducer<>(props);
        String kafkaTopicName = null;

        try {
            kafkaTopicName = System.getenv("KAFKA_TOPIC_NAME");
        } catch (NullPointerException e) {
            App.logger.error("KAFKA_TOPIC_NAME environment variable is not set.");
            System.exit(1);
        }

        EntityProducer entityProducer = new EntityProducer(kafkaProducer, kafkaTopicName);

        try {
            UUID key = UUID.randomUUID();

            Entity entity = Entity.newBuilder()
                .setGuid(key)
                .setName("Example")
                .setDescription("This is an example message")
                .build();

            App.logger.info("Producing entity: " + entity);

            entityProducer.produce(key, entity);
        } catch (Exception e) {
            App.logger.error("An error occurred while producing messages: " + e.getMessage());
        } finally {
            kafkaProducer.close();
            App.logger.info("Kafka producer closed");
        }
    }
}
