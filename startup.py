from app import create_app, init_db, run_migrations, run_tests, init_admin_user

def main():
    try:
        print("Attempting to create app with config: 'development'")
        app = create_app('development')
        
        with app.app_context():
            print("Initializing db")
            init_db()
            
            print("Running migrations...")
            run_migrations()
            print("Migrations completed successfully.")
            
            print("Running tests...")
            run_tests()
            print("Tests completed successfully.")
            
            # Initialize admin user
            init_admin_user()
            
        return app
            
    except Exception as e:
        print(f"Error during startup: {e}")
        return None
