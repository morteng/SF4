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
            
            print("Initializing admin user...")
            admin = init_admin_user()
            print(f"Admin user initialized: {admin.username}")
            
        # Run tests outside the app context since pytest will create its own
        print("Running tests...")
        run_tests()
        print("Tests completed successfully.")
            
        return app
            
    except Exception as e:
        print(f"Error during startup: {e}")
        return None

if __name__ == '__main__':
    main()
