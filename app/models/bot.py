from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bot(db.Model):
    bot_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(50), default='inactive')
    last_run = db.Column(db.DateTime, default=db.func.current_timestamp())
    error_log = db.Column(db.Text)

    def __repr__(self):
        return f"&lt;Bot {self.name}&gt;"
