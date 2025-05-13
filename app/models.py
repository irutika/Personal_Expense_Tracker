from datetime import datetime
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

    expenses = db.relationship('Expense', backref = 'owner', lazy = True)
    budgets = db.relationship('Budget', backref = 'owner', lazy = True)
    categories = db.relationship('Category', backref = "owner", lazy = True)
    settings = db.relationship("UserSettings", backref="user", uselist=False)

    budget_type = db.Column(db.String(10), default="monthy")
    monthly_reset_day = db.Column(db.Integer, default=1)
    weekly_reset_day = db.Column(db.String(10), default = "Monday" )

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    default_budget_type = db.Column(db.String(20), default="monthly")
    monthly_reset_day = db.Column(db.Integer, default=1)
    weekly_reset_day = db.Column(db.String(10), default="Monday")
    preferred_currency = db.Column(db.String(10), default="₹")
    last_reset_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Float, nullable = False)
    category = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), nullable = True)
    date = db.Column(db.DateTime, nullable = False, default = datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.String(100), nullable = False)
    amount = db.Column(db.Float, nullable= False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(10), default="custom")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='_user_category_name_uc'),)

def __repr__(self):
    return f"<Budget {self.category} - {self.amount}>"

