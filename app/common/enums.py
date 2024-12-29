from enum import Enum

class NotificationType(Enum):
    """Enumeration of all notification types in the system"""
    
    # System and Admin Actions
    ADMIN_ACTION = 'admin_action'
    SYSTEM = 'system'
    
    # Audit and Logging
    AUDIT_LOG = 'audit_log'
    CRUD_AUDIT = 'crud_audit'
    
    # User Actions
    USER_ACTION = 'user_action'
    USER_CREATED = 'user_created'
    USER_UPDATED = 'user_updated'
    USER_DELETED = 'user_deleted'
    PASSWORD_RESET = 'password_reset'
    
    # Bot Operations
    BOT_SUCCESS = 'bot_success'
    BOT_ERROR = 'bot_error'
    
    # CRUD Operations
    CRUD_CREATE = 'crud_create'
    CRUD_UPDATE = 'crud_update'
    CRUD_DELETE = 'crud_delete'

class NotificationPriority(Enum):
    """Enumeration of notification priority levels"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
