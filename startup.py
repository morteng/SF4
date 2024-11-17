from app import create_app, run_tests

def main():
    try:
        print("Attempting to create app with config: 'development'")
        app = create_app('development')
        
        # Run tests
        if not run_tests():
            print("Tests failed. Aborting startup.")
            return
        
        # Run the application
        app.run(debug=True)
        
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise

if __name__ == '__main__':
    main()
