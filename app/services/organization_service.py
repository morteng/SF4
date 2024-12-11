from app.models.organization import Organization
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

def get_all_organizations():
    try:
        return Organization.query.all()
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return []

def delete_organization(organization):
    try:
        db.session.delete(organization)
        db.session.commit()
    except SQLAlchemyError as e:
        # Log the error and possibly handle it
        print(str(e))
        db.session.rollback()

def create_organization(data):
    valid_keys = {'name', 'description', 'homepage_url'}  # Adjust based on Organization fields
    filtered_data = {k: v for k, v in data.items() if k in valid_keys}
    new_organization = Organization(**filtered_data)
    db.session.add(new_organization)
    db.session.commit()
    return new_organization

def get_organization_by_id(organization_id):
    try:
        return Organization.query.get(organization_id)
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return None

def update_organization(organization, data):
    try:
        organization.name = data.get('name', organization.name)
        organization.description = data.get('description', organization.description)
        organization.homepage_url = data.get('homepage_url', organization.homepage_url)
        db.session.commit()
        return organization
    except SQLAlchemyError as e:
        # Log the error and possibly handle it
        print(str(e))
        db.session.rollback()
        return None
