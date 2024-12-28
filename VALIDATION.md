# Validation Rules

### Notification Validation
- Validate NotificationType enum values
- Ensure related_object exists
- Validate user_id exists
- Validate message length (max 255 chars)
- Verify priority levels (low, medium, high)

### Audit Log Validation
- Validate required fields: action, ip_address, http_method, endpoint
- Verify timestamps are UTC (timezone-aware)
- Check JSON serialization of details field
- Handle errors gracefully without rollback

