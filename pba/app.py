# app.py
# flake8: noqa: E501,E305
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from .db_extensions import db
from .auth import auth_bp
from .routesincome import income_bp
from .routesexpense import expense_bp
from .routesgoal import goal_bp
from .user_profile import profile_bp
from dotenv import load_dotenv
from . import models


load_dotenv()
migrate = Migrate()

os.environ['SECRET_KEY'] = 'your_super_secret_key_here'

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///budgetmate.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_super_secret_key_here')

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db) # noqa: F841
  
    # Blueprints

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(income_bp, url_prefix='/api/income')
    app.register_blueprint(expense_bp, url_prefix='/api/expense')
    app.register_blueprint(goal_bp, url_prefix='/api/goal')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')


    @app.route('/')
    def home():
        print("✅ Home route was hit")
        return jsonify({"message": "BudgetMate Backend!"})
    
    # Optional: Create tables on app start
    with app.app_context():
        db.create_all()

    return app


# Only for local dev run
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)

app = create_app()