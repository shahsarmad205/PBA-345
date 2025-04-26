# routesincome.py
# flake8: noqa: E501,E305
from flask import Blueprint, request, jsonify
from .income import Income
from .db_extensions import db
from datetime import datetime
from .auth_middleware import token_required

income_bp = Blueprint('income', __name__)

@income_bp.route('/add', methods=['POST'])
@token_required
def add_income(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('amount') or not data.get('source') or not data.get('date'):
        return jsonify({"error": "Amount, source, and date are required"}), 400
    
    try:
        income = Income(
            user_id=current_user.id,
            amount=float(data['amount']),
            source=data['source'],
            is_recurring=data.get('is_recurring', False),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        
        db.session.add(income)
        db.session.commit()
        
        return jsonify({"message": "Income added successfully", "id": income.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@income_bp.route('/list', methods=['GET'])
@token_required
def list_income(current_user):
    try:
        incomes = Income.query.filter_by(user_id=current_user.id).all()
        
        result = []
        for income in incomes:
            result.append({
                "id": income.id,
                "amount": income.amount,
                "source": income.source,
                "is_recurring": income.is_recurring,
                "date": income.date.strftime('%Y-%m-%d')
            })
        
        return jsonify({"incomes": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500