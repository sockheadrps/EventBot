import os
import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version": 1,
    "disable_existig_Loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        },
    },
    "handlers":{
        "console": {
            'level': "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file":{
            'level': "INFO",
            "class": "logging.FileHandler",
            'filename': "Logs/infos.log",
            "mode": "w",
        },
    },
    "Loggers": {
        "bot": {
            'handlers': ['console'],
            "level": "INFO",
            "propogate": False
        },
    "discord": {
        'handlers': ['console', 'file'],
        "level": "INFO",
        "propogate": False
        },
    },

}