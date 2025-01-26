import pytest
import re
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import StaleDataError
from flask_login import login_user
from flask import get_flashed_messages
from app.models.tag import Tag
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.audit_log import AuditLog
from app.services.stipend_service import StipendService
from app.forms.admin_forms import StipendForm
from app.extensions import db
from app.constants import FlashMessages
import logging

# Configure logging
logger = logging.getLogger(__name__)
