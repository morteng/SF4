from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.configs import BaseConfig, ProductionConfig
import logging
import logging.config

app = Flask(__name__)
config = ProductionConfig(app.root_path)
app.config.from_object(config)
config.init_app(app)

# Initialize Flask-Limiter with Redis storage
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=config.STORAGE_URI,
    default_limits=["200 per day", "50 per hour"]
)

# Configure logging
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': app.config['LOG_PATH'],
            'maxBytes': 10*1024*1024,
            'backupCount': 5
        },
        'timed_file_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': app.config['LOG_PATH'],
            'when': 'H',
            'interval': 24,
            'backupCount': 24
        }
    },
    'root': {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'handlers': ['console', 'file_handler', 'timed_file_handler']
    }
})

# Final verification
from scripts.verification.verify_production_ready import verify_production_ready
if verify_production_ready():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
