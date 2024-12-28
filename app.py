from app import create_app
from flask import Flask

app = create_app()

# Verify Blueprint registration
if isinstance(app, Flask):
    registered_blueprints = [bp.name for bp in app.blueprints.values()]
    if len(registered_blueprints) != len(set(registered_blueprints)):
        # Instead of raising an error, just log it
        app.logger.warning("Duplicate Blueprint registration detected")
        # Remove duplicates
        unique_blueprints = {}
        for bp in app.blueprints.values():
            unique_blueprints[bp.name] = bp
        app.blueprints = unique_blueprints

if __name__ == '__main__':
    app.run(debug=True)
