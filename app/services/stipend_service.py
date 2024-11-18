from app.models.stipend import Stipend

def get_stipend_by_id(stipend_id):
    from app.extensions import db
    return db.session.get(Stipend, stipend_id)

def update_stipend(stipend_id, name, summary, description, homepage_url, application_procedure, eligibility_criteria, application_deadline, open_for_applications):
    from app.extensions import db
    stipend = get_stipend_by_id(stipend_id)
    if stipend:
        stipend.name = name
        stipend.summary = summary
        stipend.description = description
        stipend.homepage_url = homepage_url
        stipend.application_procedure = application_procedure
        stipend.eligibility_criteria = eligibility_criteria
        stipend.application_deadline = application_deadline
        stipend.open_for_applications = open_for_applications
        db.session.commit()
        return True
    return False

def list_all_stipends():
    from app.extensions import db
    return Stipend.query.all()
