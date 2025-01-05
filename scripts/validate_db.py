from scripts.version import validate_db_connection

if __name__ == "__main__":
    if validate_db_connection('instance/stipend.db'):
        print("Database connection validation passed")
    else:
        print("Database connection validation failed")