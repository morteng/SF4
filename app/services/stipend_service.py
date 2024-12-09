from app.models.stipend import Stipend
from app.extensions import db

def get_all_stipends():
    return Stipend.query.all()

def delete_stipend(stipend):
    db.session.delete(stipend)
    db.session.commit()

def create_stipend(data):
    if Stipend.query.filter_by(name=data['name']).first():
        print("Stipend with this name already exists.")
        return None  # or raise an exception, depending on your preference
    
    new_stipend = Stipend(**data)
    db.session.add(new_stipend)
    
    try:
        db.session.commit()
        print("Stipend added to the database successfully.")  # Debugging statement
        return new_stipend
    except Exception as e:
        print(f"Database error: {e}")  # Debugging statement
        db.session.rollback()
        return None

def get_stipend_by_id(stipend_id):
    return Stipend.query.get_or_404(stipend_id)

def update_stipend(stipend, data):
    stipend.name = data.get('name', stipend.name)
    stipend.summary = data.get('summary', stipend.summary)
    stipend.description = data.get('description', stipend.description)
    stipend.homepage_url = data.get('homepage_url', stipend.homepage_url)
    stipend.application_procedure = data.get('application_procedure', stipend.application_procedure)
    stipend.eligibility_criteria = data.get('eligibility_criteria', stipend.eligibility_criteria)
    stipend.application_deadline = data.get('application_deadline', stipend.application_deadline)
    stipend.open_for_applications = data.get('open_for_applications', stipend.open_for_applications)

    db.session.commit()
