import os 
from flask import Flask, flash, redirect, url_for, render_template
from flask_login import LoginManager  # Import LoginManager
from app.routes.visitor_routes import visitor_bp  # Import the blueprint
from app.models.user import User  # Import the User model
from app import create_app

template_dir = os.path.abspath('app/templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your_secret_key'



@app.route('/set_flash')
def set_flash():
    flash('This is a flash message!')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app = create_app()
    print(f"Serving templates from: {app.template_folder}")
    app.run(debug=True)
