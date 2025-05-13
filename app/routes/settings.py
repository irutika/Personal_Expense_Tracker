from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import UserSettings, Category
from app.routes.expenses import get_budget_start_date

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings():
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template("settings.html", user=current_user, user_settings=settings, categories=categories)

@settings_bp.route('/settings/account', methods=['POST'])
@login_required
def update_account():
    username = request.form.get('username')
    preferred_currency = request.form.get('preferred_currency')
    updated = False

    if username and username != current_user.username:
        current_user.username = username
        updated = True

    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if preferred_currency and preferred_currency != settings.preferred_currency:
        settings.preferred_currency = preferred_currency
        updated = True

    if updated:
        db.session.commit()
        flash("Account settings updated successfully!", "success")
    else:
        flash("No changes detected in account settings.", "info")

    return redirect(url_for('settings.settings'))

@settings_bp.route('/settings/budget', methods=['POST'])
@login_required
def update_budget_settings():
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    settings.default_budget_type = request.form['default_budget_type']
    settings.monthly_reset_day = int(request.form['monthly_reset_day'])
    settings.weekly_reset_day = request.form['weekly_reset_day']
    if settings.default_budget_type == "monthly":
        settings.last_reset_at = get_budget_start_date(settings, force_reset=True)
    db.session.commit()
    flash("Budget settings updated successfully!", "success")
    return redirect(url_for('settings.settings'))

@settings_bp.route('/settings/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form['name']
    if not Category.query.filter_by(name=name, user_id=current_user.id).first():
        category = Category(name=name, type="custom", user_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully!", "success")
    else:
        flash("Category already exists.", "warning")
    return redirect(url_for('settings.settings'))

@settings_bp.route('/settings/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id or category.type != "custom":
        flash("You cannot delete this category.", "danger")
        return redirect(url_for('settings.settings'))
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully!", "success")
    return redirect(url_for('settings.settings'))

@settings_bp.route('/settings/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id or category.type != "custom":
        flash("You cannot edit this category.", "danger")
        return redirect(url_for('settings.settings'))

    if request.method == 'POST':
        new_name = request.form['name']
        category.name = new_name
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for('settings.settings'))

    return render_template('edit_category.html', category=category)
