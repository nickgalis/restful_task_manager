"""
Task Management RESTful API built with Flask.

This is the main application file that defines all API endpoints
and handles request routing, validation, and error handling.
"""

from flask import Flask, request, jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_
from datetime import datetime
from database import init_db, SessionLocal
from models import User, Category, Task, TaskStatus, TaskPriority
import os

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize database on startup
with app.app_context():
    init_db()


# ============================================================================
# Helper Functions
# ============================================================================

def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the request data.
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] == '']
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None


def validate_enum_value(value, enum_class, field_name):
    """
    Validate that a value is a valid enum member.
    
    Args:
        value: Value to validate
        enum_class: Enum class to validate against
        field_name: Name of the field for error messages
        
    Returns:
        tuple: (is_valid, error_message, enum_value)
    """
    if value is None:
        return True, None, None
    
    try:
        enum_value = enum_class[value.upper()] if isinstance(value, str) else value
        return True, None, enum_value
    except (KeyError, AttributeError):
        valid_values = [e.value for e in enum_class]
        return False, f"Invalid {field_name}. Must be one of: {', '.join(valid_values)}", None


def parse_datetime(date_string):
    """
    Parse datetime string to datetime object.
    
    Args:
        date_string: Date string in ISO format
        
    Returns:
        datetime: Parsed datetime object or None
    """
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({'error': 'Bad request'}), 400


# ============================================================================
# User Endpoints
# ============================================================================

@app.route('/api/users', methods=['POST'])
def create_user():
    """
    Create a new user.
    
    Required fields: username, email
    
    Returns:
        201: User created successfully
        400: Invalid input
        500: Server error
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['username', 'email'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return jsonify(new_user.to_dict()), 201
        
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Username already exists'}), 400
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        200: User data
        404: User not found
        500: Server error
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/users', methods=['GET'])
def get_all_users():
    """
    Get all users.
    
    Returns:
        200: List of all users
        500: Server error
    """
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return jsonify([user.to_dict() for user in users]), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


# ============================================================================
# Category Endpoints
# ============================================================================

@app.route('/api/categories', methods=['POST'])
def create_category():
    """
    Create a new category.
    
    Required fields: name, user_id
    Optional fields: description
    
    Returns:
        201: Category created successfully
        400: Invalid input
        404: User not found
        500: Server error
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['name', 'user_id'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Check if user exists
        user = db.query(User).filter(User.id == data['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create new category
        new_category = Category(
            name=data['name'],
            description=data.get('description', ''),
            user_id=data['user_id']
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return jsonify(new_category.to_dict()), 201
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/categories', methods=['GET'])
def get_all_categories():
    """
    Get all categories for a user.
    
    Query parameters:
        user_id: Filter categories by user ID (optional)
        
    Returns:
        200: List of categories
        500: Server error
    """
    db = SessionLocal()
    try:
        query = db.query(Category)
        
        # Filter by user_id if provided
        user_id = request.args.get('user_id', type=int)
        if user_id:
            query = query.filter(Category.user_id == user_id)
        
        categories = query.all()
        return jsonify([category.to_dict() for category in categories]), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get a category by ID.
    
    Args:
        category_id: Category ID
        
    Returns:
        200: Category data
        404: Category not found
        500: Server error
    """
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify(category.to_dict()), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """
    Update a category.
    
    Args:
        category_id: Category ID
        
    Required fields: name, user_id
    Optional fields: description
    
    Returns:
        200: Category updated successfully
        400: Invalid input
        404: Category not found
        500: Server error
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['name', 'user_id'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Update category
        category.name = data['name']
        category.description = data.get('description', category.description)
        category.user_id = data['user_id']
        
        db.commit()
        db.refresh(category)
        
        return jsonify(category.to_dict()), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """
    Delete a category.
    
    Args:
        category_id: Category ID
        
    Returns:
        200: Category deleted successfully
        404: Category not found
        500: Server error
    """
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        db.delete(category)
        db.commit()
        
        return jsonify({'message': 'Category deleted successfully'}), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


# ============================================================================
# Task Endpoints
# ============================================================================

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """
    Create a new task.
    
    Required fields: title, category_id, user_id
    Optional fields: description, status, priority, due_date
    
    Returns:
        201: Task created successfully
        400: Invalid input
        404: User or category not found
        500: Server error
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['title', 'category_id', 'user_id'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Check if user exists
        user = db.query(User).filter(User.id == data['user_id']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if category exists
        category = db.query(Category).filter(Category.id == data['category_id']).first()
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Validate status
        status = TaskStatus.PENDING
        if 'status' in data:
            is_valid, error_msg, status = validate_enum_value(data['status'], TaskStatus, 'status')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # Validate priority
        priority = TaskPriority.MEDIUM
        if 'priority' in data:
            is_valid, error_msg, priority = validate_enum_value(data['priority'], TaskPriority, 'priority')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
        
        # Parse due_date
        due_date = parse_datetime(data.get('due_date'))
        
        # Create new task
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=status,
            priority=priority,
            due_date=due_date,
            category_id=data['category_id'],
            user_id=data['user_id']
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        return jsonify(new_task.to_dict()), 201
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """
    Get all tasks with optional filtering and sorting.
    
    Query parameters:
        status: Filter by status (pending, in_progress, completed)
        priority: Filter by priority (low, medium, high)
        category_id: Filter by category ID
        user_id: Filter by user ID
        sort_by: Sort field (due_date, created_at, priority, status) - default: created_at
        order: Sort order (asc, desc) - default: desc
        
    Returns:
        200: List of tasks
        400: Invalid query parameters
        500: Server error
    """
    db = SessionLocal()
    try:
        query = db.query(Task)
        
        # Filter by status
        status_filter = request.args.get('status')
        if status_filter:
            is_valid, error_msg, status_enum = validate_enum_value(status_filter, TaskStatus, 'status')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            query = query.filter(Task.status == status_enum)
        
        # Filter by priority
        priority_filter = request.args.get('priority')
        if priority_filter:
            is_valid, error_msg, priority_enum = validate_enum_value(priority_filter, TaskPriority, 'priority')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            query = query.filter(Task.priority == priority_enum)
        
        # Filter by category_id
        category_id = request.args.get('category_id', type=int)
        if category_id:
            query = query.filter(Task.category_id == category_id)
        
        # Filter by user_id
        user_id = request.args.get('user_id', type=int)
        if user_id:
            query = query.filter(Task.user_id == user_id)
        
        # Sorting
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc').lower()
        
        if sort_by not in ['due_date', 'created_at', 'priority', 'status', 'updated_at']:
            return jsonify({'error': 'Invalid sort_by parameter. Must be one of: due_date, created_at, priority, status, updated_at'}), 400
        
        if order not in ['asc', 'desc']:
            return jsonify({'error': 'Invalid order parameter. Must be asc or desc'}), 400
        
        # Apply sorting
        sort_column = getattr(Task, sort_by)
        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        tasks = query.all()
        return jsonify([task.to_dict() for task in tasks]), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Get a task by ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        200: Task data
        404: Task not found
        500: Server error
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify(task.to_dict()), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Full update of a task.
    
    Args:
        task_id: Task ID
        
    Required fields: title, category_id, user_id
    Optional fields: description, status, priority, due_date
    
    Returns:
        200: Task updated successfully
        400: Invalid input
        404: Task not found
        500: Server error
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['title', 'category_id', 'user_id'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate status
        if 'status' in data:
            is_valid, error_msg, status = validate_enum_value(data['status'], TaskStatus, 'status')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            task.status = status
        
        # Validate priority
        if 'priority' in data:
            is_valid, error_msg, priority = validate_enum_value(data['priority'], TaskPriority, 'priority')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            task.priority = priority
        
        # Parse due_date
        if 'due_date' in data:
            task.due_date = parse_datetime(data['due_date'])
        
        # Update task
        task.title = data['title']
        task.description = data.get('description', '')
        task.category_id = data['category_id']
        task.user_id = data['user_id']
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return jsonify(task.to_dict()), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def partial_update_task(task_id):
    """
    Partial update of a task.
    
    Args:
        task_id: Task ID
        
    Optional fields: title, description, status, priority, due_date, category_id, user_id
    
    Returns:
        200: Task updated successfully
        400: Invalid input
        404: Task not found
        500: Server error
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Update only provided fields
        if 'title' in data:
            task.title = data['title']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'status' in data:
            is_valid, error_msg, status = validate_enum_value(data['status'], TaskStatus, 'status')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            task.status = status
        
        if 'priority' in data:
            is_valid, error_msg, priority = validate_enum_value(data['priority'], TaskPriority, 'priority')
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            task.priority = priority
        
        if 'due_date' in data:
            task.due_date = parse_datetime(data['due_date'])
        
        if 'category_id' in data:
            # Verify category exists
            category = db.query(Category).filter(Category.id == data['category_id']).first()
            if not category:
                return jsonify({'error': 'Category not found'}), 404
            task.category_id = data['category_id']
        
        if 'user_id' in data:
            # Verify user exists
            user = db.query(User).filter(User.id == data['user_id']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            task.user_id = data['user_id']
        
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return jsonify(task.to_dict()), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task.
    
    Args:
        task_id: Task ID
        
    Returns:
        200: Task deleted successfully
        404: Task not found
        500: Server error
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.delete(task)
        db.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.close()


# ============================================================================
# Main
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Task Management API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'categories': '/api/categories',
            'tasks': '/api/tasks'
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
