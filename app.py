from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetmate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    employment_status = db.Column(db.String(50))
    monthly_income = db.Column(db.Float)
    income_source = db.Column(db.String(100))
    recurring_income = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user-type')
def user_type():
    return render_template('user-type.html')

# Sign-up process routes
@app.route('/signup-personal', methods=['GET', 'POST'])
def signup_personal():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup-personal.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use. Please use a different email or sign in.', 'error')
            return render_template('signup-personal.html')
        
        # Store data in session for multi-step form
        session['signup_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        }
        
        return redirect(url_for('signup_income'))
    
    return render_template('signup-personal.html')

@app.route('/signup-income', methods=['GET', 'POST'])
def signup_income():
    if 'signup_data' not in session:
        return redirect(url_for('signup_personal'))
    
    if request.method == 'POST':
        employment = request.form.get('employment')
        income = float(request.form.get('income'))
        source = request.form.get('source')
        recurring = 'recurring' in request.form
        
        # Update session data
        session['signup_data'].update({
            'employment': employment,
            'income': income,
            'source': source,
            'recurring': recurring
        })
        
        return redirect(url_for('signup_expenses'))
    
    return render_template('signup-income.html')

@app.route('/signup-expenses', methods=['GET', 'POST'])
def signup_expenses():
    if 'signup_data' not in session:
        return redirect(url_for('signup_personal'))
    
    if request.method == 'POST':
        expenses = {
            'housing': float(request.form.get('housing')),
            'utilities': float(request.form.get('utilities')),
            'transport': float(request.form.get('transport')),
            'groceries': float(request.form.get('groceries')),
            'subscriptions': float(request.form.get('subscriptions')),
            'otherExpenses': float(request.form.get('otherExpenses', 0))
        }
        
        # Update session data
        session['signup_data']['expenses'] = expenses
        
        return redirect(url_for('signup_goals'))
    
    return render_template('signup-expenses.html')

@app.route('/signup-goals', methods=['GET', 'POST'])
def signup_goals():
    if 'signup_data' not in session:
        return redirect(url_for('signup_personal'))
    
    if request.method == 'POST':
        # Handle multiple goals
        goal_names = request.form.getlist('goalName[]')
        goal_amounts = request.form.getlist('goalAmount[]')
        goal_deadlines = request.form.getlist('goalDeadline[]')
        goal_priorities = request.form.getlist('goalPriority[]')
        
        goals = []
        for i in range(len(goal_names)):
            goals.append({
                'name': goal_names[i],
                'amount': float(goal_amounts[i]),
                'deadline': goal_deadlines[i],
                'priority': goal_priorities[i]
            })
        
        # Update session data
        session['signup_data']['goals'] = goals
        
        # Create the user and associated data
        signup_data = session['signup_data']
        
        # Create user
        new_user = User(
            first_name=signup_data['first_name'],
            last_name=signup_data['last_name'],
            email=signup_data['email'],
            password_hash=generate_password_hash(signup_data['password']),
            employment_status=signup_data['employment'],
            monthly_income=signup_data['income'],
            income_source=signup_data['source'],
            recurring_income=signup_data['recurring']
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Add expenses
        for category, amount in signup_data['expenses'].items():
            expense = Expense(
                user_id=new_user.id,
                category=category,
                amount=amount
            )
            db.session.add(expense)
        
        # Add goals
        for goal_data in signup_data['goals']:
            goal = Goal(
                user_id=new_user.id,
                name=goal_data['name'],
                target_amount=goal_data['amount'],
                target_date=datetime.strptime(goal_data['deadline'], '%Y-%m-%d'),
                priority=goal_data['priority']
            )
            db.session.add(goal)
        
        db.session.commit()
        
        # Clear session data
        session.pop('signup_data', None)
        
        # Log in the user
        login_user(new_user)
        
        return redirect(url_for('dashboard'))
    
    return render_template('signup-goals.html')

@app.route('/summary')
@login_required
def summary():
    # Fetch user data for summary display
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    # Calculate total expenses
    total_expenses = sum(expense.amount for expense in expenses)
    
    # Calculate remaining income after expenses
    remaining = current_user.monthly_income - total_expenses
    
    return render_template('summary.html', 
                          user=current_user, 
                          expenses=expenses, 
                          goals=goals,
                          total_expenses=total_expenses,
                          remaining=remaining)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('signin.html')

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch user data for dashboard display
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals and statistics
    total_expenses = sum(expense.amount for expense in expenses)
    remaining = current_user.monthly_income - total_expenses
    
    # Organize expenses by category for chart
    expense_categories = {}
    for expense in expenses:
        expense_categories[expense.category] = expense.amount
    
    return render_template('dashboard.html', 
                          user=current_user, 
                          expenses=expense_categories, 
                          goals=goals,
                          total_expenses=total_expenses,
                          remaining=remaining)

# API endpoints for AJAX requests
@app.route('/api/expenses', methods=['GET', 'POST'])
@login_required
def api_expenses():
    if request.method == 'POST':
        data = request.json
        
        # Update or create new expense
        category = data.get('category')
        amount = data.get('amount')
        
        # Check if expense exists
        expense = Expense.query.filter_by(user_id=current_user.id, category=category).first()
        
        if expense:
            expense.amount = amount
        else:
            expense = Expense(user_id=current_user.id, category=category, amount=amount)
            db.session.add(expense)
        
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    # GET request - return all expenses for current user
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    expense_data = {expense.category: expense.amount for expense in expenses}
    
    return jsonify(expense_data), 200

@app.route('/api/goals', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_goals():
    if request.method == 'POST':
        data = request.json
        
        # Create new goal
        goal = Goal(
            user_id=current_user.id,
            name=data.get('name'),
            target_amount=data.get('amount'),
            target_date=datetime.strptime(data.get('deadline'), '%Y-%m-%d'),
            priority=data.get('priority')
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({'id': goal.id, 'success': True}), 200
    
    elif request.method == 'DELETE':
        goal_id = request.args.get('id')
        
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        
        if not goal:
            return jsonify({'success': False, 'message': 'Goal not found'}), 404
        
        db.session.delete(goal)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    # GET request - return all goals for current user
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    goal_data = []
    for goal in goals:
        goal_data.append({
            'id': goal.id,
            'name': goal.name,
            'amount': goal.target_amount,
            'deadline': goal.target_date.strftime('%Y-%m-%d'),
            'priority': goal.priority
        })
    
    return jsonify(goal_data), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)