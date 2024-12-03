from flask import Flask, flash, redirect, url_for, render_template
from flask_login import LoginManager  # Import LoginManager
from app.routes.visitor_routes import visitor_bp  # Import the blueprint
from app.models.user import User  # Import the User model

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Register the blueprint
app.register_blueprint(visitor_bp)

@app.route('/set_flash')
def set_flash():
    flash('This is a flash message!')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

# User loader callback function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
