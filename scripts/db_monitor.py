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
