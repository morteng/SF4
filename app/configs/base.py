from flask_config import Config

class BaseConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB

    def init_app(self, app):
        """Base configuration initialization"""
        super().init_app(app)
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True
