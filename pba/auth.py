# auth.py
# flake8: noqa: E501,E305
from flask import Blueprint, request, jsonify
from .models import User
from .db_extensions import db
import jwt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data['email']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    token = jwt.encode({
        'user.id': user.id,
        'exp': datetime.utcnow() + timedelta(days=int(os.getenv('TOKEN_EXPIRY_DAYS', 7)))
    }, os.getenv('SECRET_KEY'), algorithm='HS256')

    return jsonify({
        "message": "User created successfully",
        "token": token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode({
        'user.id': user.id,
        'exp': datetime.utcnow() + timedelta(days=int(os.getenv('TOKEN_EXPIRY_DAYS', 7)))
    }, os.getenv('SECRET_KEY'), algorithm='HS256')

    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200
