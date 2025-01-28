import sys
from pathlib import Path
import logging
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

from logging_config import LoggingConfig

def configure_logging():
    """Configure basic logging for the script"""
    logger = LoggingConfig(root_path=Path(__file__).parent.parent)
    logger.configure_logging()
    return logging.getLogger('monitoring')

def setup_dashboard(port=9100):
    app = Flask(__name__)
    metrics = PrometheusMetrics(app, path='/metrics')
    
    # Add default metrics
    metrics.info('app_info', 'Application metrics', version='1.2.11')
    
    # Create health check endpoint
    @app.route('/health')
    def health_check():
        return 'OK', 200
    
    # Start the server
    logger = configure_logging()
    logger.info(f"Starting monitoring dashboard on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    configure_logging()
    setup_dashboard()
