# migrate.py
# flake8: noqa: E501,E305
from pba.app import create_app
from pba.db_extensions import db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)
