package com.aureliusenterprise.producer;

import com.aureliusenterprise.example.Entity;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import io.confluent.kafka.serializers.schema.id.HeaderSchemaIdSerializer;
import io.confluent.kafka.serializers.subject.RecordNameStrategy;
import java.util.Properties;
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
     * Entry point for the Kafka producer application.
     *
     * @param args Command-line arguments (not used).
     */
    public static void main(String[] args) {
        // Load and validate configuration using AppConfig (similar to Pydantic Settings in Python)
        AppConfig config;
        try {
            config = AppConfig.load();
        } catch (MissingKeyException e) {
            logger.error(e.getMessage());
            System.exit(1);
            return; // Unreachable, but needed for compilation
        }

        logger.info("Configuration loaded: {}", config);

        // Initialize Kafka producer properties
        Properties props = new Properties();

        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);

        // Configure producer with validated settings from AppConfig
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, config.kafkaBootstrapServers());
        props.put("schema.registry.url", config.schemaRegistryUrl());
        props.put("value.subject.name.strategy", RecordNameStrategy.class);
        props.put("value.schema.id.serializer", HeaderSchemaIdSerializer.class);

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

        EntityProducer entityProducer = new EntityProducer(kafkaProducer, config.kafkaTopicName());

        // Start producing messages at the specified interval
        long currentTimeMillis = System.currentTimeMillis();
        App.logger.info("Starting message production on a " + config.messageIntervalMillis() + " ms interval");

        try {
            while (true) {
                // Generate a random UUID for the message key
                java.util.UUID key = java.util.UUID.randomUUID();

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
                long sleepTimeMillis = Math.max(
                    currentTimeMillis + config.messageIntervalMillis() - System.currentTimeMillis(),
                    0
                );

                App.logger.debug("Sleeping for " + sleepTimeMillis + " ms before producing the next message");
                Thread.sleep(sleepTimeMillis);

                currentTimeMillis = System.currentTimeMillis();
            }
        } catch (Exception e) {
            App.logger.error("An error occurred while producing messages: " + e.getMessage());
            Thread.currentThread().interrupt();
        } finally {
            kafkaProducer.flush();
        }
    }
}
