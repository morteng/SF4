from app.models.organization import Organization

def get_organization_by_id(organization_id):
    from app.extensions import db
    return db.session.get(Organization, organization_id)

def update_organization(organization_id, name, description, homepage_url):
    from app.extensions import db
    organization = get_organization_by_id(organization_id)
    if organization:
        organization.name = name
        organization.description = description
        organization.homepage_url = homepage_url
        db.session.commit()
        return True
    return False
