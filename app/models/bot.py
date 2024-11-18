from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    last_run = db.Column(db.DateTime, default=db.func.current_timestamp())
    error_log = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Bot(name={self.name})>"
