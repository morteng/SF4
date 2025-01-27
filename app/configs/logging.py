# Centralized logging configuration

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
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
            'level': 'WARNING',
            'formatter': 'default',
            'filename': 'app.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 3
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
