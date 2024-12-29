from app import create_app
from flask import Flask

app = create_app()

# Handle duplicate Blueprints
if isinstance(app, Flask):
    bp_names = [bp.name for bp in app.blueprints.values()]
    if len(bp_names) != len(set(bp_names)):
        app.logger.warning("Duplicate Blueprint registration detected")
        app.blueprints = {bp.name: bp for bp in app.blueprints.values()}

if __name__ == '__main__':
    app.run(debug=True)
