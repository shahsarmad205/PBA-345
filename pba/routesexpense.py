# routesexpense.py
# flake8: noqa: E501,E305

from flask import Blueprint, request, jsonify
from .expense import Expense
from .db_extensions import db
from datetime import datetime
from .auth_middleware import token_required

expense_bp = Blueprint('expense', __name__, url_prefix='/api/expense')

# Add Expense (with recurring flag)
@expense_bp.route('/', methods=['POST'])
@token_required
def add_expense(current_user):
    data = request.get_json()
    if not data.get('amount') or not data.get('category'):
        return jsonify({"error": "Amount and category are required"}), 400

    try:
        expense = Expense(
            user_id=current_user.id,
            amount=float(data['amount']),
            category=data['category'],
            description=data.get('description', ''),
            date=datetime.utcnow().date(),
            recurring=bool(data.get("recurring", False))
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify({"message": "Expense added successfully", "id": expense.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# List Expenses (with optional recurring filter)
@expense_bp.route('/', methods=['GET'])
@token_required
def list_expenses(current_user):
    try:
        recurring_param = request.args.get('recurring')
        query = Expense.query.filter_by(user_id=current_user.id)

        if recurring_param is not None:
            is_recurring = recurring_param.lower() == 'true'
            query = query.filter_by(recurring=is_recurring)

        expenses = query.order_by(Expense.date.desc()).all()

        result = [{
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "description": e.description,
            "date": e.date.strftime('%Y-%m-%d'),
            "recurring": e.recurring
        } for e in expenses]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update Expense
@expense_bp.route('/<int:expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user, expense_id):
    data = request.get_json()
    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        expense.category = data.get("category", expense.category)
        expense.amount = float(data.get("amount", expense.amount))
        expense.description = data.get("description", expense.description)
        expense.recurring = bool(data.get("recurring", expense.recurring))
        db.session.commit()
        return jsonify({"message": "Expense updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Delete Expense
@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Expense deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
