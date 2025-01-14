import unittest
from scripts.db_monitor import BackupDashboard, BackupMetric
from scripts.db_alerts import BackupAlerts
from datetime import datetime

class TestBackupMonitoring(unittest.TestCase):
    def setUp(self):
        self.dashboard = BackupDashboard()
        self.alerts = BackupAlerts()
        
    def test_metric_tracking(self):
        metric = BackupMetric(
            timestamp=datetime.now(),
            success=True,
            size_mb=500,
            duration_sec=120
        )
        self.dashboard.add_metric(metric)
        self.assertEqual(self.dashboard.metrics['success_count'], 1)
        
    def test_alert_thresholds(self):
        # Add multiple metrics to trigger alerts
        for _ in range(10):
            self.dashboard.add_metric(BackupMetric(
                timestamp=datetime.now(),
                success=False,
                size_mb=1000,
                duration_sec=600
            ))
        alerts = self.alerts._check_thresholds({
            'failure_rate': 1.0,
            'avg_duration': 600,
            'avg_size': 1000
        })
        self.assertTrue(len(alerts) > 0)

if __name__ == '__main__':
    unittest.main()
