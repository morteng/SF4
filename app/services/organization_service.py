from app.models.organization import Organization

def get_organization_by_id(organization_id):
    return Organization.query.get(organization_id)

def delete_organization(organization):
    from app.extensions import db
    db.session.delete(organization)
    db.session.commit()

def get_all_organizations():
    from app.models.organization import Organization
    return Organization.query.all()
