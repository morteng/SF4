from app import create_app, init_db, run_migrations, run_tests, init_admin_user

def main():
    # Create the Flask app with the appropriate configuration
    app = create_app()

    # Initialize the database
    with app.app_context():
        init_db()
        run_migrations()
        init_admin_user()

    # Run tests
    if not run_tests():
        print("Tests failed. Aborting startup.")
        return

    # Run the application
    app.run(debug=True)

if __name__ == '__main__':
    main()
