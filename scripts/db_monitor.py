import logging
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class BackupMetric:
    timestamp: datetime
    success: bool
    size_mb: float
    duration_sec: float
    error: Optional[str] = None

class BackupDashboard:
    """Real-time backup monitoring dashboard"""
    
    def __init__(self, max_history: int = 100):
        self.history = deque(maxlen=max_history)
        self.metrics = {
            'success_count': 0,
            'failure_count': 0,
            'total_size_mb': 0.0,
            'total_duration_sec': 0.0
        }
        
    def add_metric(self, metric: BackupMetric) -> None:
        """Add a new backup metric to the dashboard"""
        self.history.append(metric)
        
        # Update aggregate metrics
        self.metrics['total_size_mb'] += metric.size_mb
        self.metrics['total_duration_sec'] += metric.duration_sec
        
        if metric.success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['failure_count'] += 1
            logger.error(f"Backup failed: {metric.error}")
            
    def get_success_rate(self) -> float:
        """Calculate backup success rate"""
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return (self.metrics['success_count'] / total) * 100 if total > 0 else 100.0
        
    def get_avg_size(self) -> float:
        """Calculate average backup size"""
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return self.metrics['total_size_mb'] / total if total > 0 else 0.0
        
    def get_avg_duration(self) -> float:
        """Calculate average backup duration"""
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return self.metrics['total_duration_sec'] / total if total > 0 else 0.0
        
    def display(self) -> None:
        """Display current dashboard status"""
        print("\n=== Backup Monitoring Dashboard ===")
        print(f"Success Rate: {self.get_success_rate():.2f}%")
        print(f"Average Size: {self.get_avg_size():.2f} MB")
        print(f"Average Duration: {self.get_avg_duration():.2f} sec")
        print(f"Total Backups: {self.metrics['success_count'] + self.metrics['failure_count']}")
        print(f"Last Backup: {self.history[-1].timestamp if self.history else 'N/A'}")
        print("==================================\n")
import logging
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class BackupMetric:
    timestamp: datetime
    success: bool
    size_mb: float
    duration_sec: float
    error: Optional[str] = None

class BackupDashboard:
    """Real-time backup monitoring dashboard with enhanced features"""
    
    def __init__(self, max_history: int = 100):
        self.history = deque(maxlen=max_history)
        self.metrics = {
            'success_count': 0,
            'failure_count': 0,
            'total_size_mb': 0.0,
            'total_duration_sec': 0.0,
            'last_success': None,
            'last_failure': None,
            'current_status': 'idle'
        }
        self.alert_thresholds = {
            'failure_rate': 0.2,  # 20% failure rate triggers alert
            'duration_warning': 300,  # 5 minutes
            'size_warning': 1024  # 1GB
        }
        self.metrics_file = Path("backup_metrics.json")
        
    def add_metric(self, metric: BackupMetric) -> None:
        """Add a new backup metric to the dashboard with enhanced tracking"""
        self.history.append(metric)
        
        # Update aggregate metrics
        self.metrics['total_size_mb'] += metric.size_mb
        self.metrics['total_duration_sec'] += metric.duration_sec
        
        if metric.success:
            self.metrics['success_count'] += 1
            self.metrics['last_success'] = metric.timestamp
            self.metrics['current_status'] = 'healthy'
        else:
            self.metrics['failure_count'] += 1
            self.metrics['last_failure'] = metric.timestamp
            self.metrics['current_status'] = 'error'
            logger.error(f"Backup failed: {metric.error}")
            
        # Check for alerts
        self._check_alerts(metric)
        
        # Save metrics to file
        self._save_metrics()
            
    def get_success_rate(self) -> float:
        """Calculate backup success rate with error handling"""
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return (self.metrics['success_count'] / total) * 100 if total > 0 else 100.0
        
    def get_avg_size(self) -> float:
        """Calculate average backup size with error handling"""
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return self.metrics['total_size_mb'] / total if total > 0 else 0.0
        
    def get_avg_duration(self) -> float:
        """Calculate average backup duration with error handling"""
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return self.metrics['total_duration_sec'] / total if total > 0 else 0.0
        
    def display(self) -> None:
        """Display current dashboard status with enhanced formatting"""
        print("\n=== Backup Monitoring Dashboard ===")
        print(f"Success Rate: {self.get_success_rate():.2f}%")
        print(f"Average Size: {self.get_avg_size():.2f} MB")
        print(f"Average Duration: {self.get_avg_duration():.2f} sec")
        print(f"Total Backups: {self.metrics['success_count'] + self.metrics['failure_count']}")
        print(f"Last Backup: {self.history[-1].timestamp if self.history else 'N/A'}")
        print(f"Current Status: {self.metrics['current_status'].upper()}")
        print("==================================\n")
        
    def _check_alerts(self, metric: BackupMetric) -> None:
        """Check for alert conditions and trigger notifications"""
        # Check failure rate
        failure_rate = self.metrics['failure_count'] / (self.metrics['success_count'] + self.metrics['failure_count'])
        if failure_rate > self.alert_thresholds['failure_rate']:
            logger.warning(f"High failure rate detected: {failure_rate:.2%}")
            
        # Check duration
        if metric.duration_sec > self.alert_thresholds['duration_warning']:
            logger.warning(f"Long backup duration: {metric.duration_sec:.2f} sec")
            
        # Check size
        if metric.size_mb > self.alert_thresholds['size_warning']:
            logger.warning(f"Large backup size: {metric.size_mb:.2f} MB")
            
    def _save_metrics(self) -> None:
        """Save metrics to JSON file for persistence"""
        try:
            metrics_data = {
                'history': [{
                    'timestamp': m.timestamp.isoformat(),
                    'success': m.success,
                    'size_mb': m.size_mb,
                    'duration_sec': m.duration_sec,
                    'error': m.error
                } for m in self.history],
                'metrics': self.metrics,
                'alert_thresholds': self.alert_thresholds
            }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")
            
    def load_metrics(self) -> None:
        """Load metrics from JSON file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    
                # Convert history back to BackupMetric objects
                self.history = deque([
                    BackupMetric(
                        timestamp=datetime.fromisoformat(m['timestamp']),
                        success=m['success'],
                        size_mb=m['size_mb'],
                        duration_sec=m['duration_sec'],
                        error=m['error']
                    ) for m in data.get('history', [])
                ], maxlen=self.history.maxlen)
                
                # Update metrics
                self.metrics.update(data.get('metrics', {}))
                self.alert_thresholds.update(data.get('alert_thresholds', {}))
                
        except Exception as e:
            logger.error(f"Failed to load metrics: {str(e)}")

# Initialize global dashboard instance
dashboard = BackupDashboard()
