from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_user, login_required, logout_user
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "error")
    return render_template("login.html")


@auth_bp.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different email address.', 'danger')
            return redirect(url_for('auth.register'))
        
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")

        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("dashboard.dashboard"))
    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

