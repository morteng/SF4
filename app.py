from app import create_app
from flask import Flask

app = create_app()

# Verify Blueprint registration
if isinstance(app, Flask):
    registered_blueprints = [bp.name for bp in app.blueprints.values()]
    if len(registered_blueprints) != len(set(registered_blueprints)):
        raise ValueError("Duplicate Blueprint registration detected")

if __name__ == '__main__':
    app.run(debug=True)
