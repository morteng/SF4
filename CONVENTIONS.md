## Coding Conventions

### Notification Handling
- Use NotificationType enum values
- Include user_id and related_object
- Use proper priority levels
- Validate message length (max 255 chars)

### Audit Logging
- Required for all CRUD operations
- Must include: user_id, action, object_type, object_id
- Timestamps must be UTC
- Handle errors gracefully

