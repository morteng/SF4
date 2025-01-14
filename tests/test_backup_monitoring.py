import unittest
from unittest.mock import patch, MagicMock
from scripts.db_monitor import BackupDashboard, BackupMetric
from scripts.db_alerts import BackupAlerts
from datetime import datetime

class TestBackupMonitoring(unittest.TestCase):
    def setUp(self):
        self.dashboard = BackupDashboard()
        
        # Create mock config as AlertConfig instance
        self.mock_config = AlertConfig(
            email_recipients=['test@example.com'],
            smtp_server='localhost',
            smtp_port=587,
            smtp_user='user',
            smtp_password='password',
            alert_thresholds={
                'failure_rate': 0.2,
                'duration_warning': 300,
                'size_warning': 1024
            },
            notification_cooldown=300
        )
        
        # Patch the _load_config method to return our mock config
        self.patcher = patch('scripts.db_alerts.BackupAlerts._load_config', 
                           return_value=self.mock_config)
        self.mock_load_config = self.patcher.start()
        
        self.alerts = BackupAlerts()
        
    def tearDown(self):
        self.patcher.stop()
        
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
        # Mock the send_notifications method to prevent actual email sending
        with patch.object(self.alerts, '_send_notifications') as mock_send:
            alerts = self.alerts._check_thresholds({
                'failure_rate': 1.0,
                'avg_duration': 600,
                'avg_size': 1000
            })
            self.assertTrue(len(alerts) > 0)
            mock_send.assert_called_once()

if __name__ == '__main__':
    unittest.main()
