from flask import Flask
from app.configs import BaseConfig

app = Flask(__name__)
config = BaseConfig(app.root_path)
app.config.from_object(config)

# Production configuration
from scripts.path_config import configure_paths
configure_paths(production=True)
    
# Final verification
from scripts.verification.verify_production_ready import verify_production_ready
if verify_production_ready():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
