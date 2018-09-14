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
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': 'automaton.log',
            'mode': 'a',
            'formatter': 'default'
        }
    },
    'loggers': {
        'RiskExamAutomation': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        'ExamPolicy': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
})


if __name__ == "__main__":
    automaton = RiskExamAutomaton(headless=False)
    automaton.run()




