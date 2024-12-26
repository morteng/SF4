from app.extensions import db

class Organization(db.Model):
    __mapper_args__ = {'confirm_deleted_rows': False}  # Suppress delete confirmation warnings
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    homepage_url = db.Column(db.String(255), nullable=True)
    application_deadline = db.Column(db.DateTime(timezone=True), nullable=True)
    timezone = db.Column(db.String(50), nullable=True)
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
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
