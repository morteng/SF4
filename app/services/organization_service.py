from app.models.organization import Organization
from app.services.base_service import BaseService
from app.extensions import db

class OrganizationService(BaseService):
    def __init__(self):
        super().__init__(Organization)

    def get_all(self):
        """Get all organizations"""
        return self.model.query.all()

    def create(self, data, user_id=None):
        """Create a new organization"""
        try:
            organization = Organization(**data)
            db.session.add(organization)
            db.session.commit()
            return organization
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, org_id, data, user_id=None):
        """Update an existing organization"""
        organization = self.get_by_id(org_id)
        if not organization:
            return None
            
        try:
            for key, value in data.items():
                setattr(organization, key, value)
            db.session.commit()
            return organization
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self, org_id, user_id=None):
        """Delete an organization"""
        organization = self.get_by_id(org_id)
        if organization:
            try:
                db.session.delete(organization)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e
        return False

    def get_by_id(self, org_id):
        """Get a single organization by ID"""
        return self.model.query.get(org_id)
