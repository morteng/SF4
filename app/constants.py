# app/constants.py

from enum import Enum

class FlashCategory(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

class FlashMessages(str, Enum):
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
    USER_CREATED = "User created successfully."
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
    STIPEND_NOT_FOUND = "Stipend not found."
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
    CSRF_INVALID = "Invalid CSRF token. Please refresh the page and try again."

    # Audit Actions
    AUDIT_CREATE = "create"
    AUDIT_READ = "read"
    AUDIT_UPDATE = "update"
    AUDIT_DELETE = "delete"
    
    # Authentication
    USERNAME_REQUIRED = "Username is required."
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
    FORM_VALIDATION_ERROR = "Form validation failed. Please check your input."
    FORM_SUBMISSION_ERROR = "Form submission failed. Please try again."
    FORM_INVALID_CSRF = "Invalid CSRF token. Please refresh the page and try again."
    FORM_DUPLICATE_USERNAME = "Username already exists. Please choose a different username."
    FORM_DUPLICATE_EMAIL = "Email already exists. Please choose a different email address."

    # Profile Management
    UPDATE_PROFILE_SUCCESS = "Profile updated successfully."
    PROFILE_UPDATE_SUCCESS = "Profile updated successfully."
    PROFILE_UPDATE_ERROR = "Failed to update profile."
    EMAIL_ALREADY_EXISTS = "Email already exists. Please choose a different email address."
    PROFILE_UPDATE_INVALID_DATA = "Invalid data provided for profile update."
    
    # User Status Management
    USER_ACTIVATED = "User activated successfully."
    USER_DEACTIVATED = "User deactivated successfully."
    SELF_DEACTIVATION_ERROR = "Cannot deactivate your own account."
    USER_STATUS_UPDATE_ERROR = "Failed to update user status."
    PASSWORD_RESET_SUCCESS = "Password reset successfully."
    PASSWORD_RESET_ERROR = "Failed to reset password."
    USER_SEARCH_ERROR = "Failed to search users."
