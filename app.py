from app import create_app

if __name__ == '__main__':
    app = create_app()
    print(f"Serving templates from: {app.template_folder}")
    app.run(debug=True)
