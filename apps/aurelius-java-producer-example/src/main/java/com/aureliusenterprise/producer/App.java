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

/**
 * The {@link App} class is the entry point for the Aurelius Java Producer Example application.
 * It produces {@link Entity} messages to a Kafka topic at a configurable interval.
 * <p>
 * Configure the application using environment variables:
 * <ul>
 *   <li>{@code KAFKA_BOOTSTRAP_SERVERS}: Kafka bootstrap servers</li>
 *   <li>{@code SCHEMA_REGISTRY_URL}: URL for the schema registry</li>
 *   <li>{@code KAFKA_TOPIC_NAME}: Name of the Kafka topic to produce messages to</li>
 *   <li>{@code MESSAGE_INTERVAL_MILLIS}: Interval in milliseconds between messages (optional, defaults to 10000)</li>
 * </ul>
 */
public class App {

    /**
     * Logger instance for the application.
     */
    private static final Logger logger = LoggerFactory.getLogger(App.class);

    /**
     * Stores the environment variables as an unmodifiable map of key-value pairs.
     * The map is initialized from the system's environment variables at runtime.
     */
    private static final Map<String, String> env = System.getenv();

    /**
     * Entry point for the Kafka producer application.
     *
     * @param args Command-line arguments (not used).
     */
    public static void main(String[] args) {
        // Initialize Kafka producer properties
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

        // Retrieve the Kafka topic name from environment variables
        String kafkaTopicName = null;

        try {
            kafkaTopicName = App.env.get("KAFKA_TOPIC_NAME");
        } catch (NullPointerException e) {
            App.logger.error("KAFKA_TOPIC_NAME environment variable is not set.");
            System.exit(1);
        }

        // Retrieve the message interval from environment variables, defaulting to 10000 ms if not set or invalid
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

        // Create the Kafka producer instance
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

        // Start producing messages at the specified interval
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
