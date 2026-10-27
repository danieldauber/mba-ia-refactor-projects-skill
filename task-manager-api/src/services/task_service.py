from datetime import datetime

from sqlalchemy import func

from src.database import db
from src.models.task_model import Task
from src.models.user_model import User


def is_overdue(task):
    if task.due_date and task.status not in ('done', 'cancelled'):
        return task.due_date < datetime.utcnow()
    return False


def get_user_task_counts():
    """Return a dict mapping user_id → task count using a single aggregated query."""
    rows = (
        db.session.query(User.id, func.count(Task.id).label('task_count'))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .all()
    )
    return {row.id: row.task_count for row in rows}


def get_user_productivity_stats():
    """Return per-user productivity stats using a single aggregated query."""
    rows = (
        db.session.query(
            User.id,
            User.name,
            func.count(Task.id).label('total'),
            func.sum(db.case((Task.status == 'done', 1), else_=0)).label('done'),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .all()
    )
    result = []
    for row in rows:
        total = row.total or 0
        done = row.done or 0
        result.append({
            'user_id': row.id,
            'user_name': row.name,
            'total_tasks': total,
            'completed_tasks': done,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        })
    return result
