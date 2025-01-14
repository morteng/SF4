import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class AlertConfig:
    email_recipients: List[str]
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    alert_thresholds: Dict[str, float]
    notification_cooldown: int = 300  # 5 minutes in seconds

class BackupAlerts:
    """Backup alert system with multiple notification channels"""
    
    def __init__(self, config_file: str = "backup_alerts.json"):
        self.config = self._load_config(config_file)
        self.last_notification = None
        self.alert_history = []
        
    def _load_config(self, config_file: str) -> AlertConfig:
        """Load alert configuration from JSON file"""
        config_path = Path(config_file)
        if not config_path.exists():
            logger.error(f"Alert config file not found: {config_file}")
            raise FileNotFoundError(f"Alert config file not found: {config_file}")
            
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            return AlertConfig(
                email_recipients=config_data.get('email_recipients', []),
                smtp_server=config_data.get('smtp_server', 'localhost'),
                smtp_port=config_data.get('smtp_port', 587),
                smtp_user=config_data.get('smtp_user', ''),
                smtp_password=config_data.get('smtp_password', ''),
                alert_thresholds=config_data.get('alert_thresholds', {}),
                notification_cooldown=config_data.get('notification_cooldown', 300)
            )
        except Exception as e:
            logger.error(f"Failed to load alert config: {str(e)}")
            raise
            
    def check_and_notify(self, metrics: Dict) -> None:
        """Check metrics against thresholds and send notifications"""
        if self._is_in_cooldown():
            return
            
        alerts = self._check_thresholds(metrics)
        if alerts:
            self._send_notifications(alerts)
            self.last_notification = datetime.now()
            
    def _check_thresholds(self, metrics: Dict) -> List[str]:
        """Check metrics against configured thresholds"""
        alerts = []
        
        # Check failure rate
        failure_rate = metrics.get('failure_rate', 0.0)
        if failure_rate > self.config.alert_thresholds.get('failure_rate', 0.2):
            alerts.append(f"High failure rate: {failure_rate:.2%}")
            
        # Check average duration
        avg_duration = metrics.get('avg_duration', 0.0)
        if avg_duration > self.config.alert_thresholds.get('duration_warning', 300):
            alerts.append(f"Long average duration: {avg_duration:.2f} sec")
            
        # Check average size
        avg_size = metrics.get('avg_size', 0.0)
        if avg_size > self.config.alert_thresholds.get('size_warning', 1024):
            alerts.append(f"Large average size: {avg_size:.2f} MB")
            
        return alerts
        
    def _send_notifications(self, alerts: List[str]) -> None:
        """Send notifications through configured channels"""
        message = "Backup System Alerts:\n\n" + "\n".join(alerts)
        
        # Send email notifications
        if self.config.email_recipients:
            try:
                self._send_email_notification(message)
            except Exception as e:
                logger.error(f"Failed to send email notification: {str(e)}")
                
        # Log alerts
        for alert in alerts:
            logger.warning(alert)
            
        # Store alert history
        self.alert_history.append({
            'timestamp': datetime.now().isoformat(),
            'alerts': alerts
        })
        
    def _send_email_notification(self, message: str) -> None:
        """Send email notification to configured recipients"""
        msg = MIMEText(message)
        msg['Subject'] = 'Backup System Alert'
        msg['From'] = self.config.smtp_user
        msg['To'] = ', '.join(self.config.email_recipients)
        
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.smtp_user, self.config.smtp_password)
            server.sendmail(
                self.config.smtp_user,
                self.config.email_recipients,
                msg.as_string()
            )
            
    def _is_in_cooldown(self) -> bool:
        """Check if we're in notification cooldown period"""
        if self.last_notification is None:
            return False
            
        return (datetime.now() - self.last_notification).total_seconds() < self.config.notification_cooldown
        
    def get_alert_history(self) -> List[Dict]:
        """Get alert history with timestamps"""
        return self.alert_history

import argparse

def main():
    parser = argparse.ArgumentParser(description='Backup Alert System')
    parser.add_argument('--history', action='store_true', help='Show alert history')
    args = parser.parse_args()

    alerts = BackupAlerts()

    if args.history:
        for alert in alerts.get_alert_history():
            print(f"[{alert['timestamp']}]")
            for message in alert['alerts']:
                print(f" - {message}")
    else:
        print("Alert system running...")
        # Add your alert monitoring loop here

if __name__ == '__main__':
    main()
