# __init__.py
from flask import Flask
from .db_extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from .auth import auth_bp
    from .models import User # noqa: F401,E261
    from .user_profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')

    return app
