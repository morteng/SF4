from app.extensions import db

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    last_run = db.Column(db.DateTime, nullable=True)
    error_log = db.Column(db.Text, nullable=True)
