from app.extensions import db

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='inactive')

    def __repr__(self):
        return f"<Bot {self.name}>"
