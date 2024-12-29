from enum import Enum

class NotificationType(Enum):
    BOT_SUCCESS = 'bot_success'
    BOT_ERROR = 'bot_error'
    USER_ACTION = 'user_action'
    SYSTEM = 'system'
    CRUD_CREATE = 'crud_create'
    CRUD_UPDATE = 'crud_update'
    CRUD_DELETE = 'crud_delete'
    AUDIT_LOG = 'audit_log'
    USER_CREATED = 'user_created'
    USER_UPDATED = 'user_updated'
    USER_DELETED = 'user_deleted'
    PASSWORD_RESET = 'password_reset'
    ADMIN_ACTION = 'admin_action'  # Added for admin operations
    AUDIT_LOG = 'audit_log'        # Added for audit logging

class NotificationPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
