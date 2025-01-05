# Database Backup Procedure

## Manual Backup
1. Run the backup command:
   ```bash
   python -c "from scripts.version import create_db_backup; create_db_backup('instance/stipend.db')"
   ```
2. The backup will be created in the same directory as the original database with a timestamp

## Automated Backup
1. Add a cron job (Linux) or scheduled task (Windows) to run the backup daily
2. Example cron job (runs daily at 2am):
   ```bash
   0 2 * * * python -c "from scripts.version import create_db_backup; create_db_backup('instance/stipend.db')"
   ```

## Restore Procedure
1. Stop the application
2. Rename the current database file
3. Copy the backup file to the original database location
4. Restart the application

## Backup Verification
1. Check the backup file exists:
   ```bash
   ls -lh instance/*.backup_*.db
   ```
2. Verify the backup integrity:
   ```bash
   sqlite3 backup_file.db "PRAGMA integrity_check;"
   ```
