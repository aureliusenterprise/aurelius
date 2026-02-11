package com.aureliusenterprise.producer;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

import com.aureliusenterprise.example.Entity;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class EntityProducerTest {

    private static final String TEST_TOPIC = "test-topic";

    private EntityProducer entityProducer;
    private KafkaProducer<String, Entity> mockKafkaProducer;

    @SuppressWarnings("unchecked")
    @BeforeEach
    void setUp() {
        this.mockKafkaProducer = mock(KafkaProducer.class);
        this.entityProducer = new EntityProducer(this.mockKafkaProducer, TEST_TOPIC);
    }

    @Test
    void testProduceShouldSendAndFlush() {
        UUID key = UUID.randomUUID();

        Entity entity = Entity.newBuilder()
            .setGuid(key)
            .setName("Test Entity")
            .setDescription("This is a test entity")
            .build();

        assertDoesNotThrow(() -> entityProducer.produce(key, entity));

        String expectedKeyString = key.toString();
        ProducerRecord<String, Entity> expectedRecord = new ProducerRecord<>(TEST_TOPIC, expectedKeyString, entity);

        verify(mockKafkaProducer, times(1)).send(expectedRecord);
    }

    @Test
    void testProduceShouldHandleNullValue() {
        UUID key = UUID.randomUUID();
        Entity entity = null;

        assertDoesNotThrow(() -> entityProducer.produce(key, entity));

        String expectedKeyString = key.toString();
        ProducerRecord<String, Entity> expectedRecord = new ProducerRecord<>(TEST_TOPIC, expectedKeyString, entity);

        verify(mockKafkaProducer, times(1)).send(expectedRecord);
    }

    @Test
    void testProduceShouldThrowOnNullKey() {
        UUID key = null;

        Entity entity = Entity.newBuilder()
            .setGuid(UUID.randomUUID())
            .setName("Test Entity")
            .setDescription("This is a test entity")
            .build();

        assertThrows(MissingKeyException.class, () -> entityProducer.produce(key, entity));
    }
}
