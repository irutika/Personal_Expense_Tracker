from flask_login import current_user
from app.models import Category

def get_categories():
    default_categories = Category.query.filter_by(type="default").all()
    custom_categories = Category.query.filter_by(user_id=current_user.id, type="custom").all()
    return [cat.name for cat in default_categories + custom_categories]



