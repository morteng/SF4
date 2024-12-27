import logging
from datetime import datetime, timezone
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.extensions import db

class TagBot:
    def __init__(self):
        self.name = "TagBot"
        self.description = "Automatically tags stipends based on content."
        self.status = "inactive"
        self.last_run = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.keywords = {
            'Research': ['research', 'study', 'academic'],
            'Internship': ['internship', 'training', 'placement'],
            'Scholarship': ['scholarship', 'grant', 'funding'],
            'STEM': ['science', 'technology', 'engineering', 'math'],
            'Arts': ['art', 'music', 'dance', 'theater']
        }

    def run(self):
        """Run the TagBot to process and tag stipends."""
        try:
            # Add audit log
            AuditLog.create(
                user_id=0,  # System user
                action='tagbot_run',
                details='Starting TagBot execution',
                object_type='Bot'
            )
            self._start_bot()
            untagged_stipends = Stipend.query.filter(~Stipend.tags.any()).all()
            
            for stipend in untagged_stipends:
                self._process_stipend(stipend)
            
            self._complete_bot()
            
        except Exception as e:
            self._handle_error(e)

    def _start_bot(self):
        """Handle bot startup logic."""
        self.status = "active"
        self.logger.info("TagBot started.")
        AuditLog.create(
            user_id=0,
            action="bot_start",
            details=f"TagBot started at {datetime.now(timezone.utc)}",
            object_type="Bot"
        )

    def _process_stipend(self, stipend):
        """Process and tag a single stipend."""
        tags_to_add = []
        for tag_name, keyword_list in self.keywords.items():
            if self._contains_keywords(stipend, keyword_list):
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag and tag not in stipend.tags:
                    tags_to_add.append(tag)
        
        if tags_to_add:
            self._add_tags(stipend, tags_to_add)

    def _contains_keywords(self, stipend, keywords):
        """Check if stipend contains any of the given keywords."""
        content = f"{stipend.name} {stipend.description}".lower()
        return any(keyword in content for keyword in keywords)

    def _add_tags(self, stipend, tags):
        """Add tags to stipend and create audit log."""
        stipend.tags.extend(tags)
        AuditLog.create(
            user_id=0,
            action="tag_added",
            details=f"Added tags {[t.name for t in tags]} to stipend {stipend.id}",
            object_type="Stipend",
            object_id=stipend.id
        )

    def _complete_bot(self):
        """Handle bot completion logic."""
        self.status = "completed"
        self.last_run = datetime.now(timezone.utc)
        Notification.create(
            type="bot_success",
            message=f"{self.name} completed successfully"
        )
        AuditLog.create(
            user_id=0,
            action="bot_complete",
            details=f"TagBot completed at {self.last_run}",
            object_type="Bot"
        )
        db.session.commit()

    def _handle_error(self, error):
        """Handle bot errors."""
        self.status = "error"
        self.logger.error(f"Failed to run TagBot: {error}")
        Notification.create(
            type="bot_error",
            message=f"{self.name} failed: {str(error)}"
        )
        db.session.commit()
