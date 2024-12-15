from app.extensions import db

from app import db

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Tag {self.name}>'
