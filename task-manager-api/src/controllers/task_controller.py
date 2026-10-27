import logging
import re
from datetime import datetime

from src.database import db
from src.models.task_model import Task
from src.models.user_model import User
from src.models.category_model import Category
from src.config.settings import VALID_STATUSES, MIN_TITLE_LENGTH, MAX_TITLE_LENGTH, DEFAULT_PRIORITY
from src.services.notification_service import notify_task_assigned
from src.services.task_service import is_overdue

logger = logging.getLogger(__name__)


def _task_to_dict(task, include_relations=True):
    data = task.to_dict()
    data['overdue'] = is_overdue(task)
    if include_relations:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data


def get_all_tasks():
    tasks = Task.query.all()
    return [_task_to_dict(t) for t in tasks]


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return None, 'Task not found'
    return _task_to_dict(task), None


def create_task(data):
    error = _validate_task_data(data, is_create=True)
    if error:
        return None, error

    if data.get('user_id'):
        if not User.query.get(data['user_id']):
            return None, 'User not found'

    if data.get('category_id'):
        if not Category.query.get(data['category_id']):
            return None, 'Category not found'

    task = Task()
    task.title = data['title'].strip()
    task.description = data.get('description', '')
    task.status = data.get('status', 'pending')
    task.priority = data.get('priority', DEFAULT_PRIORITY)
    task.user_id = data.get('user_id')
    task.category_id = data.get('category_id')

    due_date_str = data.get('due_date')
    if due_date_str:
        parsed = _parse_date(due_date_str)
        if not parsed:
            return None, 'Invalid date format. Use YYYY-MM-DD'
        task.due_date = parsed

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info('Task created: %s - %s', task.id, task.title)

    if task.user_id and task.user:
        notify_task_assigned(task.user, task)

    return _task_to_dict(task), None


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return None, 'Task not found'

    if 'title' in data:
        title = data['title'].strip()
        if len(title) < MIN_TITLE_LENGTH:
            return None, 'Title too short'
        if len(title) > MAX_TITLE_LENGTH:
            return None, 'Title too long'
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return None, 'Invalid status'
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < 1 or data['priority'] > 5:
            return None, 'Priority must be between 1 and 5'
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            return None, 'User not found'
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            return None, 'Category not found'
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            parsed = _parse_date(data['due_date'])
            if not parsed:
                return None, 'Invalid date format'
            task.due_date = parsed
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.utcnow()
    db.session.commit()
    logger.info('Task updated: %s', task.id)
    return _task_to_dict(task), None


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return False, 'Task not found'
    db.session.delete(task)
    db.session.commit()
    logger.info('Task deleted: %s', task_id)
    return True, None


def search_tasks(query='', status='', priority='', user_id=''):
    q = Task.query
    if query:
        q = q.filter(db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%')))
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]


def get_task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(status='done').count()
    overdue_count = sum(1 for t in Task.query.all() if is_overdue(t))
    return {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': done,
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }


def _validate_task_data(data, is_create=False):
    title = data.get('title', '')
    if is_create and not title:
        return 'Title is required'
    if title:
        title = title.strip()
        if len(title) < MIN_TITLE_LENGTH:
            return 'Title too short'
        if len(title) > MAX_TITLE_LENGTH:
            return 'Title too long'
    status = data.get('status')
    if status and status not in VALID_STATUSES:
        return 'Invalid status'
    priority = data.get('priority')
    if priority is not None and (priority < 1 or priority > 5):
        return 'Priority must be between 1 and 5'
    return None


def _parse_date(date_string):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_string, fmt)
        except (ValueError, TypeError):
            continue
    return None
