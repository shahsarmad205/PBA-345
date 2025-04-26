# expense.py
# flake8: noqa: E501,E305
from datetime import datetime
from .db_extensions import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recurring = db.Column(db.Boolean, default=False, nullable=False)
    
    
    user = db.relationship('User', backref=db.backref('expenses', lazy=True))