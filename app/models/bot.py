from app.extensions import db

class Bot(db.Model):
    """Bot model representing an automated process or task."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='inactive')

    def __repr__(self):
        """Return a string representation of the Bot object."""
        return f"<Bot {self.name}>"

    def to_dict(self):
        """Convert the Bot object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }
