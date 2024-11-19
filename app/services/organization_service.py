from app.models.organization import Organization

def get_organization_by_id(organization_id):
    from app import db
    return db.session.get(Organization, organization_id)

def delete_organization(organization):
    from app import db
    db.session.delete(organization)
