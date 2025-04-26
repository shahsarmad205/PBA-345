# flake8: noqa: E501,E305
# auth_middleware.py
from functools import wraps
import os
from flask import request, jsonify
import jwt
from .models import User

SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Replace with your actual secret

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get('user.id')
            current_user = User.query.get(user_id)
            #request.user = decoded
            if not current_user:
                return jsonify({"message": "User not found!"}), 404
            
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401
        except Exception as e:
            return jsonify({"message": str(e)}), 500

        return f(current_user, *args, **kwargs)
    
       

    return decorated_function
