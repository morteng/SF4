from app.extensions import db

class Organization(db.Model):
    __mapper_args__ = {'confirm_deleted_rows': False}  # Suppress delete confirmation warnings
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    homepage_url = db.Column(db.String(255), nullable=True)  # New column
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f'<Organization {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'homepage_url': self.homepage_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
