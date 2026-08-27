from flask import Flask
from flask_migrate import Migrate
from marshmallow import ValidationError

from config import app, db, api
from models import *

@app.route('/')
def home():
    return "Hello, Flask is running!"

if __name__ == '__main__':
    # Run the app locally in debug mode
    app.run(debug=True)
