# routesgoal.py
# flake8: noqa: E501,E305
from flask import Blueprint, request, jsonify
from .goal import Goal
from .db_extensions import db
from datetime import datetime
from .auth_middleware import token_required


goal_bp = Blueprint('goal', __name__)

@goal_bp.route('/add', methods=['POST'])
@token_required
def add_goal(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('target_amount') or not data.get('priority'):
        return jsonify({"error": "Name, target amount, and priority are required"}), 400
    
    try:
        deadline = None
        if data.get('deadline'):
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
            
        goal = Goal(
            user_id=current_user.id,
            name=data['name'],
            target_amount=float(data['target_amount']),
            current_amount=float(data.get('current_amount', 0)),
            deadline=deadline,
            priority=data['priority']
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({"message": "Goal added successfully", "id": goal.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@goal_bp.route('/list', methods=['GET'])
@token_required
def list_goals(current_user):
    try:
        goals = Goal.query.filter_by(user_id=current_user.id).all()
        
        result = []
        for goal in goals:
            goal_data = {
                "id": goal.id,
                "name": goal.name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "priority": goal.priority
            }
            
            if goal.deadline:
                goal_data["deadline"] = goal.deadline.strftime('%Y-%m-%d')
            else:
                goal_data["deadline"] = None
                
            result.append(goal_data)
        
        return jsonify({"goals": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500