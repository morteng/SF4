from flask import Flask
from app.configs.base import BaseConfig, ProductionConfig, TestingConfig
from config.logging import configure_logging
