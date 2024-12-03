from flask import Flask, flash, redirect, url_for, render_template
from app.routes.visitor_routes import visitor_bp  # Import the blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register the blueprint
app.register_blueprint(visitor_bp)

@app.route('/set_flash')
def set_flash():
    flash('This is a flash message!')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
