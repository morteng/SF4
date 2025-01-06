# Deployment Checklist

def check_deployment():
    """Run deployment checks with proper error handling"""
    from scripts.version import validate_db_connection, validate_production_environment, validate_version_file
    
    print("Running deployment checks...")
    
    # Database connection check
    if not validate_db_connection('instance/stipend.db'):
        print("❌ Database connection check failed")
        return False
    print("✅ Database connection check passed")
    
    # Production environment validation
    if not validate_production_environment():
        print("❌ Production environment validation failed")
        return False
    print("✅ Production environment validation passed")
    
    # Version file validation
    if not validate_version_file():
        print("❌ Version file validation failed")
        return False
    print("✅ Version file validation passed")
    
    print("All deployment checks completed successfully")
    return True

if __name__ == "__main__":
    check_deployment()
