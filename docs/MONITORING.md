## Backup Monitoring System

### Dashboard Features
- Real-time metrics tracking
- Historical data visualization
- System status indicators
- Performance trend analysis

### Alert Configuration
1. Edit `config/backup_alerts.json`
2. Set email recipients and SMTP settings
3. Configure alert thresholds:
   - Failure rate (0.0 - 1.0)
   - Duration warning (seconds)
   - Size warning (MB)
4. Set notification cooldown (seconds)

### Usage
```bash
# Start monitoring
python scripts/db_monitor.py

# View current status
python scripts/db_monitor.py --status

# Check alert history
python scripts/db_alerts.py --history
```
