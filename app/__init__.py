from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hadr'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.expenses import expenses_bp
    from .routes.settings import settings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp) 

    with app.app_context():
        db.create_all()
        seed_default_categories()

    return app

def seed_default_categories():
    from app.models import Category
    default_names = ['Food', 'Transport', 'Utilities', 'Entertainment']
    for name in default_names:
        if not Category.query.filter_by(name=name, type = "default").first():
            db.session.add(Category(name=name, type="default"))
    db.session.commit()