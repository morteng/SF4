from flask import Flask

app = Flask(__name__)

# Initialize the app
app.config = BaseConfig(str(app.root_path))

if __name__ == '__main__':
    app.run()
