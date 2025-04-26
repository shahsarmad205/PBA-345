# routesgoal.py
# flake8: noqa: E501,E305
from flask import Blueprint, request, jsonify
from .goal import Goal
from .db_extensions import db
from datetime import datetime
from .auth_middleware import token_required


goal_bp = Blueprint('goal', __name__, url_prefix='/api/goal')

@goal_bp.route('/', methods=['GET', 'POST'])
@token_required
def handle_goals(current_user):
    if request.method == 'GET':
        # same as your list_goals code
        goals = Goal.query.filter_by(user_id=current_user.id).all()
        result = []
        for goal in goals:
            goal_data = {
                "id": goal.id,
                "name": goal.name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "priority": goal.priority,
                "deadline": goal.deadline.strftime('%Y-%m-%d') if goal.deadline else None,
                "completed": False
            }
            result.append(goal_data)
        return jsonify(result)

    if request.method == 'POST':
        # same as your add_goal code
        data = request.get_json()
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

@goal_bp.route('/<int:goal_id>', methods=['PUT'])
@token_required
def update_goal(current_user, goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    data = request.get_json()
    
    if 'completed' in data:
        goal.completed = bool(data['completed'])
    
    db.session.commit()
    return jsonify({"message": "Goal updated successfully"}), 200
