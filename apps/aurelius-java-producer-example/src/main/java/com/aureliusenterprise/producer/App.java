package com.aureliusenterprise.producer;

import com.aureliusenterprise.example.Entity;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger logger = LoggerFactory.getLogger(App.class);
    private static final Map<String, String> env = System.getenv();

    public static void main(String[] args) {
        Properties props = new Properties();

        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);

        try {
            props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, App.env.get("KAFKA_BOOTSTRAP_SERVERS"));
        } catch (NullPointerException e) {
            App.logger.error("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.");
            System.exit(1);
        }

        try {
            props.put("schema.registry.url", App.env.get("SCHEMA_REGISTRY_URL"));
        } catch (NullPointerException e) {
            App.logger.error("SCHEMA_REGISTRY_URL environment variable is not set.");
            System.exit(1);
        }

        String kafkaTopicName = null;

        try {
            kafkaTopicName = App.env.get("KAFKA_TOPIC_NAME");
        } catch (NullPointerException e) {
            App.logger.error("KAFKA_TOPIC_NAME environment variable is not set.");
            System.exit(1);
        }

        long intervalMillis = 10000;

        try {
            intervalMillis = Long.parseLong(App.env.get("MESSAGE_INTERVAL_MILLIS"));
        } catch (NullPointerException e) {
            App.logger.warn(
                "MESSAGE_INTERVAL_MILLIS environment variable is not set. Using default of " + intervalMillis + " ms."
            );
        } catch (NumberFormatException e) {
            App.logger.warn("Invalid MESSAGE_INTERVAL_MILLIS value. Using default of " + intervalMillis + " ms.");
        }

        KafkaProducer<String, Entity> kafkaProducer = new KafkaProducer<>(props);

        // Add shutdown hook for graceful shutdown
        Runtime.getRuntime().addShutdownHook(
            new Thread(() -> {
                App.logger.info("Shutting down gracefully...");
                kafkaProducer.close();
                App.logger.info("Kafka producer closed");
            })
        );

        EntityProducer entityProducer = new EntityProducer(kafkaProducer, kafkaTopicName);

        long currentTimeMillis = System.currentTimeMillis();
        App.logger.info("Starting message production on a " + intervalMillis + " ms interval");

        try {
            while (true) {
                // Generate a random UUID for the message key
                UUID key = UUID.randomUUID();

                // Create an example Entity message
                Entity entity = Entity.newBuilder()
                    .setGuid(key)
                    .setName("Example")
                    .setDescription("This is an example message")
                    .build();

                // Produce the message to Kafka
                App.logger.info("Producing entity: " + entity);
                entityProducer.produce(key, entity);

                // Wait for the specified interval before producing the next message
                long sleepTimeMillis = Math.max(currentTimeMillis + intervalMillis - System.currentTimeMillis(), 0);

                App.logger.debug("Sleeping for " + sleepTimeMillis + " ms before producing the next message");
                Thread.sleep(sleepTimeMillis);

                currentTimeMillis = System.currentTimeMillis();
            }
        } catch (Exception e) {
            App.logger.error("An error occurred while producing messages: " + e.getMessage());
            Thread.currentThread().interrupt();
        }
    }
}
