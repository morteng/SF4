import os
import string
import secrets
import json
import re

from datetime import datetime, timezone
from typing import Any, Union, Tuple
from functools import wraps
from urllib.parse import urlparse

from flask import abort, redirect, url_for, flash, request, current_app, render_template
from flask_login import current_user, login_required as flask_login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import generate_csrf
from bleach import clean as bleach_clean
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from croniter import croniter

from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.user import User
from app.extensions import db
from app.constants import FlashMessages, FlashCategory
from contextlib import contextmanager

# Logger initialization moved to LoggingConfig
from app.configs.logging_config import LoggingConfig
logger = LoggingConfig(None).logger  # Temporary fix - proper initialization will be handled in app setup
