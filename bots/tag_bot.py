import logging
from datetime import datetime
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.extensions import db

class TagBot:
    def __init__(self):
        self.name = "TagBot"
        self.description = "Automatically tags stipends based on content."
        self.status = "inactive"
        self.last_run = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def run(self):
        """Run the TagBot to process and tag stipends."""
        try:
            self.status = "active"
            self.logger.info("TagBot started.")
            
            # Create audit log for bot start
            AuditLog.create(
                user_id=0,  # System user
                action="bot_start",
                details=f"TagBot started at {datetime.now(timezone.utc)}",
                object_type="Bot",
                object_id=self.id
            )
            
            # Create audit log for bot start
            from app.models.audit_log import AuditLog
            AuditLog.create(
                user_id=0,  # System user
                action="bot_start",
                details=f"TagBot started at {datetime.utcnow()}",
                object_type="Bot",
                object_id=self.id
            )
            
            # Get untagged stipends
            from app.models.stipend import Stipend
            from app.models.tag import Tag
            untagged_stipends = Stipend.query.filter(~Stipend.tags.any()).all()
            
            # Basic tagging logic
            for stipend in untagged_stipends:
                # Enhanced tagging logic
                tags_to_add = []
            
                # Check for multiple keywords
                keywords = {
                    'Research': ['research', 'study', 'academic'],
                    'Internship': ['internship', 'training', 'placement'],
                    'Scholarship': ['scholarship', 'grant', 'funding']
                }
            
                for tag_name, keyword_list in keywords.items():
                    if any(keyword in stipend.description.lower() for keyword in keyword_list):
                        tag = Tag.query.filter_by(name=tag_name).first()
                        if tag and tag not in stipend.tags:
                            tags_to_add.append(tag)
            
                # Add all matching tags
                if tags_to_add:
                    stipend.tags.extend(tags_to_add)
                    # Create audit log for each tag addition
                    AuditLog.create(
                        user_id=0,  # System user
                        action="tag_added",
                        details=f"Added tags {[t.name for t in tags_to_add]} to stipend {stipend.id}",
                        object_type="Stipend",
                        object_id=stipend.id
                    )
            
            db.session.commit()
                
            self.status = "completed"
            self.last_run = datetime.utcnow()
            
            # Create success notification
            notification = Notification(
                message=f"{self.name} completed successfully",
                type="bot_success",
                read_status=False
            )
            db.session.add(notification)
            
            # Create audit log for bot completion
            AuditLog.create(
                user_id=0,  # System user
                action="bot_complete",
                details=f"TagBot completed at {datetime.utcnow()}",
                object_type="Bot",
                object_id=self.id
            )
            
            db.session.commit()
            
        except Exception as e:
            self.status = "error"
            self.logger.error(f"Failed to run TagBot: {e}")
            
            # Create error notification
            notification = Notification(
                message=f"{self.name} failed: {str(e)}",
                type="bot_error",
                read_status=False
            )
            db.session.add(notification)
            db.session.commit()
