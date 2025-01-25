import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for monitoring verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_monitoring_dashboards(verify_tests=True):
    """Verify monitoring dashboards configuration with enhanced metrics"""
    logger = configure_logger()
    try:
        # Verify dashboard configuration
        dashboard_path = Path('monitoring/dashboard.json')
        
        # Collect real-time stats
        import psutil
        stats = {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'processes': len(psutil.pids()),
            'network': psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        }
        
        # Enhanced metrics based on MANAGER.txt priorities
        required_metrics = [
            'cpu', 'memory', 'disk', 'requests',
            'db_connections',  # Database reliability
            'response_time',   # Performance monitoring
            'error_rate',      # Stability monitoring
            'backup_status',   # Backup system health
            'security_events', # Security monitoring
            'active_users',    # User activity tracking
            'api_usage',       # API monitoring
            'bot_activity',    # Bot performance
            'stipend_updates', # Stipend activity
            'test_coverage',   # Test coverage
            'failed_tests',    # Test failures
            'pending_updates', # System updates
            'security_audit'   # Security audit status
        ]
        if not dashboard_path.exists():
            logger.error("Dashboard configuration not found")
            return False
            
        # Verify dashboard contains required metrics
        import json
        with open(dashboard_path) as f:
            dashboard = json.load(f)
            
        required_metrics = [
            'cpu', 'memory', 'disk', 'requests',
            'db_connections',  # Database reliability
            'response_time',   # Performance monitoring
            'error_rate',      # Stability monitoring
            'backup_status',   # Backup system health
            'security_events', # Security monitoring
            'active_users',    # User activity tracking
            'api_usage',       # API monitoring
            'bot_activity',    # Bot performance
            'stipend_updates', # Stipend activity
            'test_coverage',   # Test coverage
            'failed_tests',    # Test failures
            'pending_updates', # System updates
            'security_audit'   # Security audit status
        ]
        missing_metrics = [m for m in required_metrics if m not in dashboard.get('metrics', [])]
        
        if missing_metrics:
            logger.error(f"Dashboard missing required metrics: {', '.join(missing_metrics)}")
            return False
            
        logger.info("Dashboard configuration verified")
        return True
    except Exception as e:
        logger.error(f"Dashboard verification failed: {str(e)}")
        return False

def verify_monitoring_setup():
    """Verify production monitoring configuration"""
    logger = configure_logger()
    
    try:
        # Verify required monitoring environment variables with defaults
        required_vars = {
            'MONITORING_ENABLED': 'true',
            'METRICS_ENDPOINT': '/metrics',
            'ALERTING_ENABLED': 'true',
            'MONITORING_INTERVAL': '60',
            'ALERT_THRESHOLDS': 'cpu:90,memory:90,disk:90',
            'ADMIN_MONITORING_ENABLED': 'true',
            'USER_ACTIVITY_TRACKING': 'true',
            'ERROR_TRACKING_ENABLED': 'true'
        }
        
        # Set default values if not present
        for var, default in required_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
                logger.info(f"Set default value for {var}: {default}")
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing monitoring environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify monitoring directory exists
        monitoring_dir = Path('monitoring')
        if not monitoring_dir.exists():
            logger.warning("Monitoring directory not found - creating...")
            try:
                monitoring_dir.mkdir(parents=True, exist_ok=True)
                (monitoring_dir / 'dashboard.json').touch()
                (monitoring_dir / 'alerts.json').touch()
                (monitoring_dir / 'metrics.py').touch()
                logger.info("Created monitoring directory with default files")
            except Exception as e:
                logger.error(f"Failed to create monitoring directory: {str(e)}")
                return False
            
        # Verify required monitoring files
        required_files = [
            'monitoring/dashboard.json',
            'monitoring/alerts.json',
            'monitoring/metrics.py'
        ]
        
        missing_files = [f for f in required_files if not Path(f).exists()]
        if missing_files:
            logger.error(f"Missing monitoring files: {', '.join(missing_files)}")
            return False
            
        logger.info("Monitoring setup verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Monitoring verification failed: {str(e)}")
        return False

    # New response time check
    try:
        response = test_client.get('/')
        if response.headers.get('X-Response-Time') is None:
            logger.error("Missing X-Response-Time header")
            return False
    except Exception as e:
        logger.error(f"Response time check failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_monitoring_setup():
        print("Monitoring verification passed")
        exit(0)
    else:
        print("Monitoring verification failed")
        exit(1)
