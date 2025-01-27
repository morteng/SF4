from flask import Config

class BaseConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    
    def __init__(self, root_path):
        super().__init__(root_path)
        self.init_app()
    
    def init_app(self):
        """Base configuration initialization"""
        self.root_path = self.root_path
        self.jinja_env.trim_blocks = True
        self.jinja_env.lstrip_blocks = True
