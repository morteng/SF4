from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Ensure db is defined here or imported properly

stipend_tag_association = db.Table(
    'stipend_tag_association',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)
