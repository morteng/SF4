from app import create_app, db

def init_db(app):
    with app.app_context():
        db.create_all()

def run_migrations():
    # Run migrations if needed
    pass

def run_tests():
    # Run tests if needed
    pass

def main():
    app = create_app('development')
    init_db(app)
    run_migrations()
    run_tests()
    app.run(debug=True)

if __name__ == '__main__':
    main()
