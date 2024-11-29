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
    new_organization = Organization(**data)
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
