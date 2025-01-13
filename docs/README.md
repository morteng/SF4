# Stipend Discovery Website

## Version 1.2.11

This is a Flask-based web application for discovering and managing stipend opportunities.

### Deployment Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Configure paths: `python scripts/path_config.py --production`
3. Initialize database: `python scripts/startup/init_db.py --production`
4. Start application: `python app.py`
5. Verify production readiness: `python scripts/verification/verify_production_ready.py --production`

### Troubleshooting
If you encounter import errors:
1. Verify virtual environment is activated
2. Check Python path configuration
3. Ensure all dependencies are installed

### Key Features
- Tag-based filtering
- Admin interface
- Automated bots
- Comprehensive testing
- Enhanced security settings
- Improved monitoring
- Robust deployment verification
