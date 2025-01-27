from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.models import db
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)

class StipendService:
    def __init__(self):
        self.metrics = {
            'success_count': 0,
            'error_count': 0,
            'last_operation': None
        }

    def create(self, data, user_id=None):
        """Create stipend with only name required per management directive"""
        try:
            # Validate only required field
            if 'name' not in data or not data['name']:
                raise ValueError("Name is required")
                
            # Set defaults for optional fields
            data.setdefault('summary', '')
            data.setdefault('description', '')
            data.setdefault('homepage_url', '')
            data.setdefault('organization_id', None)
            data.setdefault('tags', [])
            data.setdefault('application_procedure', '')
            data.setdefault('eligibility_criteria', '')
            data.setdefault('application_deadline', None)
            data.setdefault('open_for_applications', True)
            
            # Create the stipend
            stipend = Stipend()
            stipend.update(data, user_id)
            db.session.add(stipend)
            db.session.commit()
            logger.info(f"Stipend created successfully: {stipend.id}")
            return stipend
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating stipend: {str(e)}")
            raise

    def update(self, id, data, user_id=None):
        """Update stipend fields with audit logging and validation"""
        try:
            stipend = self.get(id)
            
            # Handle tags separately
            if 'tags' in data:
                tags = data.pop('tags')
                stipend.tags = [Tag.query.get(tag_id) for tag_id in tags]
            
            # Update other fields
            stipend.update(data, user_id)
            db.session.commit()
            return stipend
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating stipend {id}: {str(e)}")
            raise

    def get(self, id):
        return Stipend.query.get(id)

    def delete(self, id, user_id=None):
        """Delete a stipend with audit logging"""
        try:
            stipend = self.get(id)
            db.session.delete(stipend)
            db.session.commit()
            return stipend
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting stipend {id}: {str(e)}")
            raise

    def parse_flexible_date(self, date_str):
        """Parse flexible date formats into datetime objects"""
        if not date_str:
            return None
        
        try:
            # Try parsing as full datetime first
            dt = parse(date_str)
            
            # Handle vague descriptions like "in August"
            if 'in ' in date_str.lower():
                month = date_str.lower().split('in ')[1].strip()
                dt = parse(month)
                # Set to end of month if only month is specified
                dt = dt + relativedelta(day=31)
                
            # Handle month/year format
            elif len(date_str.split()) == 2 and not date_str[-1].isdigit():
                dt = parse(date_str)
                dt = dt + relativedelta(day=31)
                
            # Handle year only
            elif len(date_str) == 4 and date_str.isdigit():
                dt = parse(date_str)
                dt = dt + relativedelta(month=12, day=31)
                
            # Validate the parsed date
            if dt.year < 1900 or dt.year > 2100:
                return None
                
            return dt.replace(tzinfo=datetime.utcnow().tzinfo)
        except ValueError:
            return None
