# app/constants.py

from enum import Enum

# Form validation messages
MISSING_FIELD_ERROR = "This field is required."
MISSING_REQUIRED_FIELD = "This field is required"
INVALID_DATETIME_FORMAT = "Invalid date/time format. Please use YYYY-MM-DD HH:MM:SS"


class NotificationType(Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SUCCESS = 'success'

class NotificationPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class FlashCategory(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

    INVALID_DATE_RANGE = "Date must be between {min_date} and {max_date}."
    INVALID_TIME_RANGE = "Time must be between {start_time} and {end_time}."
    INVALID_TIME_COMPONENTS = "Invalid time values. Hours must be 0-23, minutes and seconds 0-59."
    INVALID_LEAP_YEAR_DATE = "Invalid date for February in non-leap years."
    INVALID_DATE_VALUES = "Invalid date values. Please check the day, month, and year."
    
    # CSRF
    
    # General
    GENERIC_SUCCESS = "Operation completed successfully."
    GENERIC_ERROR = "An error occurred. Please try again."

    # CRUD Operations
    CREATE_SUCCESS = "Record created successfully."
    READ_SUCCESS = "Record retrieved successfully."
    UPDATE_SUCCESS = "Record updated successfully."
    DELETE_SUCCESS = "Record deleted successfully."
    CREATE_ERROR = "Error creating record."
    READ_ERROR = "Error retrieving record."
    UPDATE_ERROR = "Error updating record."
    DELETE_ERROR = "Error deleting record."
    
    # User Management
    USER_CREATED = "User {username} created successfully."
    NOT_FOUND = "{entity_name} not found."
    CREATE_USER_SUCCESS = "User created successfully."
    USER_UPDATED = "User updated successfully."
    USER_DELETED = "User deleted successfully."
    USERNAME_ALREADY_EXISTS = "Username already exists. Please choose a different username."
    CREATE_USER_ERROR = "Failed to create user: "
    CREATE_USER_INVALID_DATA = "Invalid data provided for user creation."
    UPDATE_USER_SUCCESS = "User updated successfully."
    UPDATE_USER_ERROR = "Failed to update user."
    DELETE_USER_SUCCESS = "User deleted successfully."
    DELETE_USER_ERROR = "Failed to delete user."
    USER_NOT_FOUND = "User not found."
    
    # Profile Management
    EMAIL_REQUIRED = "Email is required."
    EMAIL_INVALID = "Invalid email address."
    EMAIL_LENGTH = "Email cannot exceed 100 characters."
    EMAIL_ALREADY_EXISTS = "Email already exists. Please choose a different email address."
    USERNAME_REQUIRED = "Username is required."
    PROFILE_UPDATE_SUCCESS = "Profile updated successfully."
    PROFILE_UPDATE_ERROR = "Failed to update profile."
    PROFILE_UPDATE_INVALID_DATA = "Invalid data provided for profile update."

    # Bot Management
    CREATE_BOT_SUCCESS = "Bot created successfully."
    BOT_RUN_STARTED = "Bot run started successfully."
    BOT_RUN_COMPLETED = "Bot run completed successfully."
    BOT_RUN_FAILED = "Bot run failed."
    BOT_SCHEDULED = "Bot scheduled successfully."
    CREATE_BOT_ERROR = "Failed to create bot: "
    CREATE_BOT_INVALID_DATA = "Invalid data provided for bot creation."
    UPDATE_BOT_SUCCESS = "Bot updated successfully."
    UPDATE_BOT_ERROR = "Failed to update bot."
    DELETE_BOT_SUCCESS = "Bot deleted successfully."
    DELETE_BOT_ERROR = "Failed to delete bot."
    BOT_NOT_FOUND = "Bot not found."
    BOT_SCHEDULED_SUCCESS = "Bot scheduled successfully."
    BOT_RUN_SUCCESS = "Bot run completed successfully."
    BOT_RUN_ERROR = "Bot run failed."

    # Organization Management
    CREATE_ORGANIZATION_SUCCESS = "Organization created successfully."
    CREATE_ORGANIZATION_ERROR = "Failed to create organization: "
    CREATE_ORGANIZATION_INVALID_FORM = "Invalid data provided for organization creation."
    CREATE_ORGANIZATION_DUPLICATE_ERROR = "An organization with this name already exists."
    CREATE_ORGANIZATION_DATABASE_ERROR = "Database error while creating organization."
    UPDATE_ORGANIZATION_SUCCESS = "Organization updated successfully."
    UPDATE_ORGANIZATION_ERROR = "Failed to update organization."
    UPDATE_ORGANIZATION_INVALID_FORM = "Invalid data provided for organization update."
    UPDATE_ORGANIZATION_DATABASE_ERROR = "Database error while updating organization."
    DELETE_ORGANIZATION_SUCCESS = "Organization deleted successfully."
    DELETE_ORGANIZATION_DATABASE_ERROR = "Database error while deleting organization."
    ORGANIZATION_NOT_FOUND = "Organization not found."
    INVALID_URL_FORMAT = "URL must start with http:// or https://."
    INVALID_FUTURE_DATE = "Date must be in the future."
    INVALID_PAST_DATE = "Date must be in the past."
    ORGANIZATION_CREATE_SUCCESS = "Organization created successfully."
    ORGANIZATION_UPDATE_SUCCESS = "Organization updated successfully."
    ORGANIZATION_DELETE_SUCCESS = "Organization deleted successfully."
    ORGANIZATION_DUPLICATE_NAME = "An organization with this name already exists."
    ORGANIZATION_INVALID_DATA = "Invalid organization data provided."

    # Form Validation Messages
    NAME_REQUIRED = "Stipend name is required."
    NAME_LENGTH = "Stipend name cannot exceed 100 characters."
    # Name validation message moved to FlashMessages enum to avoid duplication
    FORM_FIELD_REQUIRED = "{field} is required."
    FORM_INVALID_URL = "{field} must be a valid URL starting with http:// or https://."
    FORM_INVALID_DATE_FORMAT = "{field} must be in the format YYYY-MM-DD HH:MM:SS."
    FORM_INVALID_CHARACTERS = "{field} contains invalid characters."

    # Stipend Management
    CREATE_STIPEND_SUCCESS = "Stipend created successfully."
    CREATE_STIPEND_ERROR = "Failed to create stipend."
    UPDATE_STIPEND_SUCCESS = "Stipend updated successfully."
    UPDATE_STIPEND_ERROR = "Failed to update stipend."
    INVALID_DATE_FORMAT = "Invalid date format. Please use YYYY-MM-DD HH:MM:SS."
    INVALID_TIME_VALUES = "Invalid time values. Hours must be 0-23, minutes and seconds 0-59."
    DATE_REQUIRED = "Date is required."
    DELETE_STIPEND_SUCCESS = "Stipend deleted successfully."
    DELETE_STIPEND_ERROR = "Failed to delete stipend."
    INVALID_ORGANIZATION = "Invalid organization selected. Please choose a valid organization."

    # Tag Management
    CREATE_TAG_SUCCESS = "Tag created successfully."
    CREATE_TAG_ERROR = "Failed to create tag: "
    UPDATE_TAG_SUCCESS = "Tag updated successfully."
    UPDATE_TAG_ERROR = "Failed to update tag."
    DELETE_TAG_SUCCESS = "Tag deleted successfully."
    DELETE_TAG_ERROR = "Failed to delete tag."

    # CSRF
    CSRF_ERROR = "Invalid CSRF token. Please refresh the page and try again."
    ACCESS_DENIED = "Access denied. You don't have permission to perform this action."
    RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later."

    # Audit Actions
    AUDIT_CREATE = "create"
    AUDIT_READ = "read"
    AUDIT_UPDATE = "update"
    AUDIT_DELETE = "delete"
    AUDIT_LOG_SUCCESS = "Action logged successfully."
    AUDIT_LOG_ERROR = "Action was successful but audit logging failed. Please check system logs."
    
    # Stipend Management
    STIPEND_CREATE_SUCCESS = "Stipend created successfully."
    STIPEND_UPDATE_SUCCESS = "Stipend updated successfully."
    STIPEND_DELETE_SUCCESS = "Stipend deleted successfully."
    STIPEND_CREATE_ERROR = "Failed to create stipend."
    STIPEND_UPDATE_ERROR = "Failed to update stipend."
    STIPEND_DELETE_ERROR = "Failed to delete stipend."
    STIPEND_NOT_FOUND = "Stipend not found."
    
    # Notification Types
    NOTIFICATION_STIPEND_CREATED = "stipend_created"
    NOTIFICATION_STIPEND_UPDATED = "stipend_updated"
    NOTIFICATION_STIPEND_DELETED = "stipend_deleted"
    
    # Authentication
    ADMIN_ACCESS_ERROR = "Error accessing admin panel. Please try again."
    USERNAME_LENGTH = "Username must be between 3 and 50 characters."
    USERNAME_FORMAT = "Username can only contain letters, numbers and underscores."
    LOGIN_SUCCESS = "Logged in successfully."
    LOGIN_ERROR = "Invalid username or password."
    LOGOUT_SUCCESS = "Logged out successfully."
    REGISTER_SUCCESS = "Registered successfully."
    REGISTER_ERROR = "Registration failed. Please try again."
    LOGIN_INVALID_CREDENTIALS = "Invalid username or password."
    PASSWORD_WEAK = "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character."

    # Form Validation
    FORM_SUBMISSION_ERROR = "Form submission failed. Please try again."
    FORM_INVALID_CSRF = "Invalid CSRF token. Please refresh the page and try again."
    FORM_DUPLICATE_USERNAME = "Username already exists. Please choose a different username."
    
    # CRUD Operation Messages
    CRUD_VALIDATION_ERROR = "Validation failed: {errors}"
    CRUD_OPERATION_ERROR = "Operation failed: {error}"
    CRUD_RECORD_NOT_FOUND = "{entity} not found."
    CRUD_PERMISSION_DENIED = "You don't have permission to perform this action."
    
    # Template Management
    TEMPLATE_NOT_FOUND = "Template not found."
    TEMPLATE_ERROR = "Error rendering template."

    # Backup/Restore Messages
    BACKUP_STARTED = "Database backup started"
    BACKUP_SUCCESS = "Database backup completed successfully"
    BACKUP_FAILED = "Database backup failed: {error}"
    RESTORE_STARTED = "Database restore started"
    RESTORE_SUCCESS = "Database restore completed successfully"
    RESTORE_FAILED = "Database restore failed: {error}"
    BACKUP_VALIDATION_SUCCESS = "Backup validation successful"
    BACKUP_VALIDATION_FAILED = "Backup validation failed: {error}"
    BACKUP_FILE_NOT_FOUND = "Backup file not found: {filename}"
    BACKUP_INTEGRITY_CHECK_FAILED = "Backup integrity check failed"
    BACKUP_SCHEDULE_UPDATED = "Backup schedule updated successfully"
    BACKUP_SCHEDULE_UPDATE_FAILED = "Failed to update backup schedule: {error}"
    BACKUP_RETENTION_POLICY_UPDATED = "Backup retention policy updated"
    INVALID_BACKUP_FILE = "Invalid backup file format"
    BACKUP_ALREADY_RUNNING = "Backup operation already in progress"
    RESTORE_CONFIRMATION_REQUIRED = "Restore operation requires confirmation"
    RESTORE_CANCELLED = "Restore operation cancelled"
    BACKUP_STORAGE_LIMIT_EXCEEDED = "Backup storage limit exceeded"

    # Profile Management
    UPDATE_PROFILE_SUCCESS = "Profile updated successfully."
    
    # User Status Management
    USER_ACTIVATED = "User activated successfully."
    USER_DEACTIVATED = "User deactivated successfully."
    SELF_DEACTIVATION_ERROR = "Cannot deactivate your own account."
    USER_STATUS_UPDATE_ERROR = "Failed to update user status."
    PASSWORD_RESET_SUCCESS = "Password reset successfully."
    PASSWORD_RESET_ERROR = "Failed to reset password."
    USER_SEARCH_ERROR = "Failed to search users."
class RouteMessages(str, Enum):
    ROUTE_REGISTRATION_ERROR = "Failed to register route: {route_name}"
    ROUTE_REGISTERED = "Successfully registered route: {route_name}"
    MISSING_BLUEPRINT = "Missing blueprint for route registration"

class FlashMessages(str, Enum):
    GENERIC_ERROR = "An error occurred. Please try again."
    TEMPLATE_ERROR = "Error loading template. Please try again later."
    ADMIN_ACCESS_ERROR = "You don't have permission to access this page."
    INVALID_NAME_CHARACTERS = "Name can only contain letters, numbers, spaces, hyphens, and basic punctuation."
    INVALID_STIPEND_NAME_CHARACTERS = "Stipend name can only contain letters, numbers, spaces, hyphens, and basic punctuation."
    INVALID_DATE_FORMAT = "Invalid date format. Please use YYYY-MM-DD HH:MM:SS."
    UPDATE_ERROR = "Failed to update record."
    DELETE_ERROR = "Failed to delete record."
    INVALID_LEAP_YEAR_DATE = "Invalid date for February in non-leap years."
    NOT_FOUND = "{entity_name} not found."
    CREATE_SUCCESS = "Record created successfully."
    UPDATE_SUCCESS = "Record updated successfully."
    DELETE_SUCCESS = "Record deleted successfully."
    CREATE_ERROR = "Error creating record."
    INVALID_TIME_FORMAT = "Invalid time format. Please use HH:MM:SS."
    INVALID_TIME_RANGE = "Time must be between {start_time} and {end_time}."
    MISSING_DATE_FIELD = "Date is required."
    MISSING_TIME_FIELD = "Time is required."
    FUTURE_DATE_REQUIRED = "Date must be in the future."
    PAST_DATE_REQUIRED = "Date must be in the past."
    INVALID_DATE_VALUES = "Invalid date values. Please check the day, month, and year."
    INVALID_TIME_COMPONENTS = "Invalid time values. Hours must be 0-23, minutes and seconds 0-59."
    MISSING_FIELD_ERROR = "This field is required."
    EMAIL_REQUIRED = "Email is required."
    EMAIL_INVALID = "Invalid email address."
    EMAIL_LENGTH = "Email cannot exceed 100 characters."
    EMAIL_ALREADY_EXISTS = "Email already exists. Please choose a different email address."
    USERNAME_REQUIRED = "Username is required."
    USERNAME_LENGTH = "Username must be between 3 and 50 characters."
    USERNAME_FORMAT = "Username can only contain letters, numbers, and underscores."
    NAME_REQUIRED = "Name is required."
    NAME_LENGTH = "Name cannot exceed 100 characters."
    INVALID_URL = "Please enter a valid URL starting with http:// or https://."
    INVALID_DATETIME_FORMAT = "Invalid date/time format. Please use YYYY-MM-DD HH:MM:SS."
    FORM_VALIDATION_ERROR = "Form validation failed. Please check your input."
    DATE_REQUIRED = "Date is required."
    CSRF_ERROR = "Invalid CSRF token. Please refresh the page and try again."
