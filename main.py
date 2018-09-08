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
        }
    },
    'loggers': {
        'RiskExamAutomation': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
})


if __name__ == "__main__":
    automaton = RiskExamAutomaton(headless=False)
    automaton.run()




