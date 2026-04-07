package com.aureliusenterprise.producer;

import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Type-safe configuration class for the Kafka producer application.
 * Uses environment variables with automatic validation, similar to Pydantic Settings in Python.
 * <p>
 * Configure using environment variables:
 * <ul>
 *   <li>{@code KAFKA_BOOTSTRAP_SERVERS}: Kafka bootstrap servers (required)</li>
 *   <li>{@code SCHEMA_REGISTRY_URL}: URL for the schema registry (required)</li>
 *   <li>{@code KAFKA_TOPIC_NAME}: Name of the Kafka topic to produce messages to (required)</li>
 *   <li>{@code MESSAGE_INTERVAL_MILLIS}: Interval in milliseconds between messages (optional, defaults to 10000)</li>
 * </ul>
 */
public record AppConfig(
    String kafkaBootstrapServers,
    String schemaRegistryUrl,
    String kafkaTopicName,
    long messageIntervalMillis
) {
    private static final Logger logger = LoggerFactory.getLogger(AppConfig.class);

    /**
     * Creates a new {@link AppConfig} instance by loading configuration from environment variables.
     * Uses type-safe binding with validation, similar to Pydantic Settings in Python.
     *
     * @return a configured {@link AppConfig} instance
     * @throws MissingKeyException if any required configuration is missing or invalid
     */
    public static AppConfig load() {
        Map<String, String> env = System.getenv();

        String kafkaBootstrapServers;
        try {
            kafkaBootstrapServers = getRequiredString(env, "KAFKA_BOOTSTRAP_SERVERS");
        } catch (MissingKeyException e) {
            AppConfig.logger.error("Failed to load KAFKA_BOOTSTRAP_SERVERS: " + e.getMessage());
            throw e;
        }

        String schemaRegistryUrl;
        try {
            schemaRegistryUrl = getRequiredString(env, "SCHEMA_REGISTRY_URL");
        } catch (MissingKeyException e) {
            AppConfig.logger.error("Failed to load SCHEMA_REGISTRY_URL: " + e.getMessage());
            throw e;
        }

        String kafkaTopicName;
        try {
            kafkaTopicName = getRequiredString(env, "KAFKA_TOPIC_NAME");
        } catch (MissingKeyException e) {
            AppConfig.logger.error("Failed to load KAFKA_TOPIC_NAME: " + e.getMessage());
            throw e;
        }

        long messageIntervalMillis = getOptionalLong(env, "MESSAGE_INTERVAL_MILLIS", 10_000);

        return new AppConfig(kafkaBootstrapServers, schemaRegistryUrl, kafkaTopicName, messageIntervalMillis);
    }

    /**
     * Gets a required string value from the environment.
     *
     * @param env the environment map
     * @param key the environment variable name
     * @return the string value
     * @throws MissingKeyException if the value is missing or empty
     */
    private static String getRequiredString(Map<String, String> env, String key) {
        String value = env.get(key);
        if (value == null || value.isBlank()) {
            throw new MissingKeyException(
                "Environment variable " + key + " is required but was not set. Please check your configuration."
            );
        }
        return value;
    }

    /**
     * Gets an optional long value from the environment, with a default fallback.
     *
     * @param env the environment map
     * @param key the environment variable name
     * @param defaultValue the default value if not set or invalid
     * @return the parsed long value or the default
     */
    private static long getOptionalLong(Map<String, String> env, String key, long defaultValue) {
        String value = env.get(key);
        if (value == null || value.isBlank()) {
            logger.warn("Environment variable " + key + " is not set. Using default of " + defaultValue + " ms.");
            return defaultValue;
        }
        try {
            long parsedValue = Long.parseLong(value);
            if (parsedValue < 0) {
                logger.warn(key + " value must be non-negative. Using default of " + defaultValue + " ms.");
                return defaultValue;
            }
            return parsedValue;
        } catch (NumberFormatException e) {
            logger.warn("Invalid " + key + " value '" + value + "'. Using default of " + defaultValue + " ms.");
            return defaultValue;
        }
    }
}
