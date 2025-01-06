import os
import sys
import subprocess
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect

def verify_database_connection(db_url):
    """Verify database connection and schema version"""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            inspector = inspect(engine)
            if 'alembic_version' not in inspector.get_table_names():
                print("Error: Alembic version table not found")
                return False
                
            result = conn.execute("SELECT version_num FROM alembic_version")
            version = result.scalar()
            print(f"Current database version: {version}")
            return True
            
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False

def verify_alembic_migrations():
    """Verify Alembic migrations are up to date"""
    try:
        alembic_cfg = Config("migrations/alembic.ini")
        command.upgrade(alembic_cfg, 'head')
        return True
    except Exception as e:
        print(f"Alembic migration error: {str(e)}")
        return False

def verify_environment_variables():
    """Verify required environment variables are set"""
    required_vars = [
        'SQLALCHEMY_DATABASE_URI',
        'SECRET_KEY',
        'ADMIN_EMAIL',
        'ADMIN_PASSWORD',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def verify_security_settings():
    """Verify security-related settings"""
    try:
        if os.getenv('FLASK_DEBUG') == '1':
            print("Warning: Debug mode is enabled in production")
            return False
            
        if len(os.getenv('SECRET_KEY', '')) < 32:
            print("Error: SECRET_KEY is too short")
            return False
            
        return True
    except Exception as e:
        print(f"Security verification error: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("Starting production verification...")
    
    # Get database URL from environment
    db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not db_url:
        print("Error: SQLALCHEMY_DATABASE_URI not set")
        sys.exit(1)
        
    # Run verification steps
    if not verify_environment_variables():
        sys.exit(1)
        
    if not verify_security_settings():
        sys.exit(1)
        
    if not verify_database_connection(db_url):
        sys.exit(1)
        
    if not verify_alembic_migrations():
        sys.exit(1)
        
    print("Production verification completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
