from flask import Flask
from app.config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)

# Production configuration
from scripts.path_config import configure_paths
configure_paths(production=True)
    
# Initialize production logging
from scripts.init_logging import configure_logging
configure_logging(production=True)
    
# Final verification
from scripts.verification.verify_production_ready import verify_production_ready
if verify_production_ready():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
