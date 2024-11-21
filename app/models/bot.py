from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50))
    last_run = db.Column(db.DateTime)
    error_log = db.Column(db.Text)
