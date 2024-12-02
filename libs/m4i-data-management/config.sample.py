import sys

'''
LOGGING CONFIG
'''
logging_config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'filename': 'log/default.log',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'backupCount': 7,
            'when': 'midnight'
        }
    },
    'loggers': {
        'm4i_data_management': {
            'level': 'DEBUG',
            'handlers': ['debug', 'default']
        }
    }
}


'''
CONNECTOR CONFIG
'''
config = {
    "confluent.kafka.bootstrap.servers": "YOUR_BOOTSTRAP_SERVER",
    "confluent.kafka.group.id": "YOUR_GROUP_ID",
    "confluent.schema.registry.url": "YOUR_SCHEMA_REGISTRY_URL",
    "elastic.cloud.scheme": "https",
    "elastic.cloud.port": 9243,
}
