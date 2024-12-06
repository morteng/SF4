from app.models.organization import Organization
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

def get_all_organizations():
    """Retrieve all organizations."""
    try:
        return Organization.query.all()
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return []

def delete_organization(organization):
    """Delete the specified organization."""
    try:
        db.session.delete(organization)
        db.session.commit()
    except SQLAlchemyError as e:
        # Log the error and possibly handle it
        print(str(e))
        db.session.rollback()

def create_organization(data):
    """Create a new organization."""
    new_organization = Organization(**data)
    db.session.add(new_organization)
    db.session.commit()
    return new_organization

def get_organization_by_id(organization_id):
    """Retrieve an organization by its ID."""
    try:
        return Organization.query.get(organization_id)
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return None

def update_organization(organization, data):
    """Update the specified organization with new data."""
    organization.name = data['name']
    organization.description = data['description']
    organization.homepage_url = data['homepage_url']
    db.session.commit()
