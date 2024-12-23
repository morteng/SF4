# app/constants.py

# Flash Message Categories
FLASH_CATEGORY_SUCCESS = "success"
FLASH_CATEGORY_ERROR = "error"
FLASH_CATEGORY_INFO = "info"
FLASH_CATEGORY_WARNING = "warning"

# Flash Messages
FLASH_MESSAGES = {
    # General
    "GENERIC_SUCCESS": "Operation completed successfully.",
    "GENERIC_ERROR": "An error occurred. Please try again.",

    # User Management
    "CREATE_USER_SUCCESS": "User created successfully.",
    "USERNAME_ALREADY_EXISTS": "Username already exists. Please choose a different username.",
    "CREATE_USER_ERROR": "Failed to create user: ",
    "CREATE_USER_INVALID_DATA": "Invalid data provided for user creation.",
    "UPDATE_USER_SUCCESS": "User updated successfully.",
    "UPDATE_USER_ERROR": "Failed to update user.",
    "DELETE_USER_SUCCESS": "User deleted successfully.",
    "DELETE_USER_ERROR": "Failed to delete user.",
    "USER_NOT_FOUND": "User not found.",

    # Bot Management
    "CREATE_BOT_SUCCESS": "Bot created successfully.",
    "CREATE_BOT_ERROR": "Failed to create bot: ",
    "CREATE_BOT_INVALID_DATA": "Invalid data provided for bot creation.",
    "UPDATE_BOT_SUCCESS": "Bot updated successfully.",
    "UPDATE_BOT_ERROR": "Failed to update bot.",
    "DELETE_BOT_SUCCESS": "Bot deleted successfully.",
    "DELETE_BOT_ERROR": "Failed to delete bot.",
    "BOT_NOT_FOUND": "Bot not found.",

    # Organization Management
    "CREATE_ORGANIZATION_SUCCESS": "Organization created successfully.",
    "CREATE_ORGANIZATION_ERROR": "Failed to create organization: ",
    "CREATE_ORGANIZATION_INVALID_FORM": "Invalid data provided for organization creation.",
    "CREATE_ORGANIZATION_DATABASE_ERROR": "Database error while creating organization.",  
    "UPDATE_ORGANIZATION_SUCCESS": "Organization updated successfully.",
    "UPDATE_ORGANIZATION_ERROR": "Failed to update organization.",
    "UPDATE_ORGANIZATION_INVALID_FORM": "Invalid data provided for organization update.",
    "UPDATE_ORGANIZATION_DATABASE_ERROR": "Database error while updating organization.",  
    "DELETE_ORGANIZATION_SUCCESS": "Organization deleted successfully.",
    "DELETE_ORGANIZATION_DATABASE_ERROR": "Database error while deleting organization.",
    "ORGANIZATION_NOT_FOUND": "Organization not found.",

    # Stipend Management
    "CREATE_STIPEND_SUCCESS": "Stipend created successfully.",
    "CREATE_STIPEND_ERROR": "Failed to create stipend.",
    "UPDATE_STIPEND_SUCCESS": "Stipend updated successfully.",
    "UPDATE_STIPEND_ERROR": "Failed to update stipend.", 
    "INVALID_DATE_FORMAT": "Invalid date format. Please use YYYY-MM-DD HH:MM:SS.",  
    "STIPEND_NOT_FOUND": "Stipend not found.",
    "DELETE_STIPEND_SUCCESS": "Stipend deleted successfully.",
    "DELETE_STIPEND_ERROR": "Failed to delete stipend.",

    # Tag Management
    "CREATE_TAG_SUCCESS": "Tag created successfully.",
    "CREATE_TAG_ERROR": "Failed to create tag: ",
    "UPDATE_TAG_SUCCESS": "Tag updated successfully.",
    "UPDATE_TAG_ERROR": "Failed to update tag.",
    "DELETE_TAG_SUCCESS": "Tag deleted successfully.",
    "DELETE_TAG_ERROR": "Failed to delete tag.",

    # Authentication
    "LOGIN_SUCCESS": "Logged in successfully.",
    "LOGIN_ERROR": "Invalid username or password.",
    "LOGOUT_SUCCESS": "Logged out successfully.",
    "REGISTER_SUCCESS": "Registered successfully.",
    "REGISTER_ERROR": "Registration failed. Please try again.",
    "LOGIN_INVALID_CREDENTIALS": "Invalid username or password.",

    # Profile Management
    "UPDATE_PROFILE_SUCCESS": "Profile updated successfully.",
    "PROFILE_UPDATE_SUCCESS": "Profile updated successfully.",
    "PROFILE_UPDATE_ERROR": "Failed to update profile.",
    "PROFILE_UPDATE_INVALID_DATA": "Invalid data provided for profile update."
}
