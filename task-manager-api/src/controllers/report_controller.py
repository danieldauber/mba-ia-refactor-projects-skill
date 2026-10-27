import logging
from datetime import datetime, timedelta

from src.database import db
from src.models.task_model import Task
from src.models.user_model import User
from src.models.category_model import Category
from src.services.task_service import is_overdue, get_user_productivity_stats

logger = logging.getLogger(__name__)


def get_summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    all_tasks = Task.query.all()
    overdue_list = []
    for t in all_tasks:
        if is_overdue(t):
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (datetime.utcnow() - t.due_date).days,
            })

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    user_stats = get_user_productivity_stats()

    done = Task.query.filter_by(status='done').count()
    return {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'done': done,
            'cancelled': Task.query.filter_by(status='cancelled').count(),
        },
        'tasks_by_priority': {
            'critical': Task.query.filter_by(priority=1).count(),
            'high': Task.query.filter_by(priority=2).count(),
            'medium': Task.query.filter_by(priority=3).count(),
            'low': Task.query.filter_by(priority=4).count(),
            'minimal': Task.query.filter_by(priority=5).count(),
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.query.filter(Task.created_at >= seven_days_ago).count(),
            'tasks_completed_last_7_days': Task.query.filter(
                Task.status == 'done', Task.updated_at >= seven_days_ago
            ).count(),
        },
        'user_productivity': user_stats,
    }


def get_user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, 'User not found'

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = pending = in_progress = cancelled = overdue = high_priority = 0

    for t in tasks:
        if t.status == 'done':
            done += 1
        elif t.status == 'pending':
            pending += 1
        elif t.status == 'in_progress':
            in_progress += 1
        elif t.status == 'cancelled':
            cancelled += 1
        if t.priority <= 2:
            high_priority += 1
        if is_overdue(t):
            overdue += 1

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        },
    }, None

