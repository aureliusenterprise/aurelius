package com.aureliusenterprise.producer;

public class MissingKeyException extends RuntimeException {

    public MissingKeyException(String message) {
        super(message);
    }
}
