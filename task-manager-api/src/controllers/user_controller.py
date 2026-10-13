import logging
import re

from src.database import db
from src.models.user_model import User
from src.models.task_model import Task
from src.config.settings import VALID_ROLES, MIN_PASSWORD_LENGTH

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def get_all_users():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = Task.query.filter_by(user_id=u.id).count()
        result.append(data)
    return result


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, 'User not found'
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data, None


def create_user(data):
    error = _validate_user_data(data, is_create=True)
    if error:
        return None, error

    if User.query.filter_by(email=data['email']).first():
        return None, 'Email already registered'

    user = User()
    user.name = data['name']
    user.email = data['email']
    user.set_password(data['password'])
    user.role = data.get('role', 'user')

    db.session.add(user)
    db.session.commit()
    logger.info('User created: %s - %s', user.id, user.name)
    return user.to_dict(), None


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return None, 'User not found'

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not _EMAIL_RE.match(data['email']):
            return None, 'Invalid email'
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return None, 'Email already registered'
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return None, 'Password too short'
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return None, 'Invalid role'
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict(), None


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return False, 'User not found'

    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    logger.info('User deleted: %s', user_id)
    return True, None


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, 'User not found'

    from datetime import datetime
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data['overdue'] = (
            t.due_date < datetime.utcnow()
            if t.due_date and t.status not in ('done', 'cancelled')
            else False
        )
        result.append(data)
    return result, None


def login(data):
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return None, 'Email and password are required'

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, 'Invalid credentials'

    if not user.active:
        return None, 'User inactive'

    return {'user': user.to_dict()}, None


def _validate_user_data(data, is_create=False):
    if is_create:
        if not data.get('name'):
            return 'Name is required'
        if not data.get('email'):
            return 'Email is required'
        if not data.get('password'):
            return 'Password is required'

    if data.get('email') and not _EMAIL_RE.match(data['email']):
        return 'Invalid email'

    if data.get('password') and len(data['password']) < MIN_PASSWORD_LENGTH:
        return 'Password too short'

    if data.get('role') and data['role'] not in VALID_ROLES:
        return 'Invalid role'

    return None
