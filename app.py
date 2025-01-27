from flask import Flask
from app.configs import BaseConfig, ProductionConfig
import logging
import logging.config

app = Flask(__name__)
config = ProductionConfig(app.root_path)
app.config.from_object(config)
config.init_app(app)

# Final verification
from scripts.verification.verify_production_ready import verify_production_ready
if verify_production_ready():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
