from flask import Flask
from flask_login import LoginManager
from app import create_app
from app.models.user import User

app = create_app()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
