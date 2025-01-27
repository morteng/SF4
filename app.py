from flask import Flask
from app.configs import ProductionConfig

app = Flask(__name__)
config = ProductionConfig(app.root_path)
app.config.from_object(config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
