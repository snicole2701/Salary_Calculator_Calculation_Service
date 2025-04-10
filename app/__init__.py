from flask import Flask
from .routes import calculation_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(calculation_bp)
    return app

