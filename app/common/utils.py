from datetime import datetime
import pytz
import logging
from app.constants import FlashMessages
from wtforms.validators import ValidationError

from flask import Blueprint, current_app
from app.extensions import db  # Changed import source

logger = logging.getLogger(__name__)

class BaseBlueprint(Blueprint):
    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)
