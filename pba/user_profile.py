# user_profile.py
# flake8: noqa: E501,E305
from flask import Blueprint, request, jsonify
#from flask_login import current_user
from .db_extensions import db  
from .models import User
from .auth_middleware import token_required

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile_bp.route('/', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.first_name,
        "salary": current_user.salary,
        "monthly_income": current_user.monthly_income,
        "address": current_user.address,
        "state": current_user.state,
        "zip": current_user.zip_code
    })

@profile_bp.route('/', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.json
    user = current_user

    allowed_fields = ['email', 'first_name', 'last_name', 'salary', 'monthly_income', 'address', 'state', 'zip_code']

    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify({"message": "Profile updated"})
