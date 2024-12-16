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
    "CREATE_USER_ERROR": "Failed to create user.",
    "UPDATE_USER_SUCCESS": "User updated successfully.",
    "UPDATE_USER_ERROR": "Failed to update user.",
    "DELETE_USER_SUCCESS": "User deleted successfully.",
    "DELETE_USER_ERROR": "Failed to delete user.",

    # Tag Management
    "CREATE_TAG_SUCCESS": "Tag created successfully.",
    "CREATE_TAG_ERROR": "Failed to create tag: Database error.",
    "UPDATE_TAG_SUCCESS": "Tag updated successfully.",
    "UPDATE_TAG_ERROR": "Failed to update tag: Database error.",
    "DELETE_TAG_SUCCESS": "Tag deleted successfully.",
    "DELETE_TAG_ERROR": "Failed to delete tag.",

    # Stipend Management
    "CREATE_STIPEND_SUCCESS": "Stipend created successfully.",
    "CREATE_STIPEND_ERROR": "Stipend creation failed due to invalid input.",
    "UPDATE_STIPEND_SUCCESS": "Stipend updated successfully.",
    "UPDATE_STIPEND_ERROR": "Failed to update stipend: Database error.",
    "DELETE_STIPEND_SUCCESS": "Stipend deleted successfully.",
    "DELETE_STIPEND_ERROR": "Failed to delete stipend.",

    # Organization Management
    "CREATE_ORGANIZATION_SUCCESS": "Organization created successfully.",
    "CREATE_ORGANIZATION_ERROR": "Failed to create organization: Database error.",
    "UPDATE_ORGANIZATION_SUCCESS": "Organization updated successfully.",
    "UPDATE_ORGANIZATION_ERROR": "Failed to update organization: Database error.",
    "DELETE_ORGANIZATION_SUCCESS": "Organization deleted successfully.",
    "DELETE_ORGANIZATION_ERROR": "Failed to delete organization.",

    # Bot Management
    "CREATE_BOT_SUCCESS": "Bot created successfully.",
    "CREATE_BOT_ERROR": "Failed to create bot.",
    "UPDATE_BOT_SUCCESS": "Bot updated successfully.",
    "UPDATE_BOT_ERROR": "Failed to update bot.",
    "DELETE_BOT_SUCCESS": "Bot deleted successfully.",
    "DELETE_BOT_ERROR": "Failed to delete bot.",
    "RUN_BOT_SUCCESS": "Bot ran successfully.",
    "RUN_BOT_ERROR": "Failed to run bot.",

    # Authentication
    "LOGIN_SUCCESS": "Logged in successfully.",
    "LOGIN_ERROR": "Invalid username or password.",
    "LOGOUT_SUCCESS": "Logged out successfully.",
    "REGISTER_SUCCESS": "Registered successfully.",
    "REGISTER_ERROR": "Registration failed. Please try again.",

    # Profile Management
    "UPDATE_PROFILE_SUCCESS": "Profile updated successfully.",
    "UPDATE_PROFILE_ERROR": "Failed to update profile.",

    # Others
    # Add more messages as needed
}
