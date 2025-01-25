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
    # Production configuration
    from scripts.path_config import configure_paths
    configure_paths(production=True)
    
    # Initialize production logging
    from scripts.init_logging import init_logging
    init_logging(production=True)
    
    # Final verification
    from scripts.verification.verify_production_ready import verify_production_ready
    if verify_production_ready():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
