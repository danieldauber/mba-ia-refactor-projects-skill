import logging

from src.database import db
from src.models.category_model import Category
from src.models.task_model import Task
from src.config.settings import DEFAULT_COLOR

logger = logging.getLogger(__name__)


def get_all_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return result


def create_category(data):
    name = data.get('name')
    if not name:
        return None, 'Name is required'

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_COLOR)

    db.session.add(category)
    db.session.commit()
    return category.to_dict(), None


def update_category(cat_id, data):
    cat = Category.query.get(cat_id)
    if not cat:
        return None, 'Category not found'

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    db.session.commit()
    return cat.to_dict(), None


def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return False, 'Category not found'

    db.session.delete(cat)
    db.session.commit()
    return True, None
