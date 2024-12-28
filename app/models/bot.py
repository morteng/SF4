from app.extensions import db

class Bot(db.Model):
    __mapper_args__ = {"confirm_deleted_rows": False}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='inactive')
    def __repr__(self):
        return f"<Bot {self.name}>"
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }
