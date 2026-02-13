package com.aureliusenterprise.producer;

/**
 * Exception thrown when a required key is missing during processing.
 */
public class MissingKeyException extends RuntimeException {

    /**
     * Constructs a new {@link MissingKeyException} with the specified detail message.
     *
     * @param message the detail message explaining the reason for the exception
     */
    public MissingKeyException(String message) {
        super(message);
    }
}
