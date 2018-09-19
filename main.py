#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
from examautomaton import RiskExamAutomaton

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        },
        'rotate_file': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'automaton.log',
            'encoding': 'utf8',
            'when': 'D',
            'interval': 30
        },
        'errors': {
            'level': 'ERROR',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'automaton_error.log',
            'encoding': 'utf8',
            'maxBytes': 102400000,
            'backupCount': 30
        }
    },
    'loggers': {
        'RiskExamAutomaton': {
            'level': 'DEBUG'
        },
        '': {
            'level': 'INFO',
            'handlers': ['console', 'rotate_file', 'errors']
        }
    }
})

if __name__ == "__main__":
    automaton = RiskExamAutomaton(headless=False)
    try:
        automaton.run()
    except Exception as e:
        logging.error(e, exc_info=True)
