from app import db

# Define your association tables here
stipend_tag_association = db.Table(
    'stipend_tag',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Add other association tables as needed
