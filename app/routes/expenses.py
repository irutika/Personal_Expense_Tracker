from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Expense, UserSettings, Budget
from categories import get_categories
from datetime import datetime, timedelta, date
import calendar
from collections import defaultdict

expenses_bp = Blueprint('expenses', __name__)

def get_budget_start_date(user_settings, force_reset=False):
    now = datetime.now()
    if not user_settings:
        return now.replace(day=1)

    if user_settings.default_budget_type == "monthly":
        reset_day = min(user_settings.monthly_reset_day, calendar.monthrange(now.year, now.month)[1])

        # If we are forcing a reset or the current day is on or after the reset day,
        # the start date is the reset day of the current month.
        if force_reset or now.day >= reset_day:
            return now.replace(day=reset_day, hour=0, minute=0, second=0, microsecond=0)
        else:
            # If the current day is before the reset day, the last reset was on
            # the reset day of the previous month.
            prev_month = now.replace(day=1) - timedelta(days=1)
            prev_month_reset_day = min(user_settings.monthly_reset_day, calendar.monthrange(prev_month.year, prev_month.month)[1])
            return prev_month.replace(day=prev_month_reset_day, hour=0, minute=0, second=0, microsecond=0)

    elif user_settings.default_budget_type == "weekly":
        weekday_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        reset_day_index = weekday_map.get(user_settings.weekly_reset_day, 0)
        days_since_reset = (now.weekday() - reset_day_index) % 7
        start_date = now - timedelta(days=days_since_reset)
        return start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    elif user_settings.default_budget_type == "yearly":
        last_reset = user_settings.last_reset_at or now
        return last_reset.replace(hour=0, minute=0, second=0, microsecond=0)

    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def should_reset_budget(user_settings):
    now = datetime.now()
    last_reset = user_settings.last_reset_at or datetime.min

    if user_settings.default_budget_type == "monthly":
        reset_day = user_settings.monthly_reset_day or 1
        this_month_reset_date = datetime(now.year, now.month, min(reset_day, calendar.monthrange(now.year, now.month)[1]))
        return now.date() >= this_month_reset_date.date() and last_reset.date() < this_month_reset_date.date()

    elif user_settings.default_budget_type == "weekly":
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        target_weekday = days.index(user_settings.weekly_reset_day or "Monday")
        delta_days = (now.weekday() - target_weekday) % 7
        this_week_reset_date = now - timedelta(days=delta_days)
        return last_reset.date() < this_week_reset_date.date()

    elif user_settings.default_budget_type == "yearly":
        return last_reset.year < now.year

    return False

def get_next_budget_reset_date(user_settings):
    now = datetime.now()
    if user_settings.default_budget_type == "weekly":
        weekday_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        reset_day_index = weekday_map.get(user_settings.weekly_reset_day, 0)
        days_ahead = (reset_day_index - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return now + timedelta(days=days_ahead)

    elif user_settings.default_budget_type == "monthly":
        reset_day = user_settings.monthly_reset_day
        year = now.year
        month = now.month
        if now.day >= reset_day:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
        day = min(reset_day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day)

    elif user_settings.default_budget_type == "yearly":
        last_reset = user_settings.last_reset_at or now
        return last_reset.replace(year=last_reset.year + 1)

    return now

@expenses_bp.route("/expenses")
@login_required
def expenses():
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()

    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()

    # Check if the budget should be reset based on the current date and last reset
    if should_reset_budget(user_settings):
        user_settings.last_reset_at = get_budget_start_date(user_settings)
        db.session.commit()

    last_reset = user_settings.last_reset_at
    next_reset_date = get_next_budget_reset_date(user_settings)

    user_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= last_reset
    ).all()

    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    currency_symbol = user_settings.preferred_currency or "₹"

    category_totals = {}
    for expense in user_expenses:
        category_totals.setdefault(expense.category, 0)
        category_totals[expense.category] += float(expense.amount)

    category_status = []
    for budget in budgets:
        budget_amount = float(budget.amount)
        spent = float(category_totals.get(budget.category, 0))
        percent_used = (spent / budget_amount) * 100 if budget_amount > 0 else 0
        percent_used = min(percent_used, 100)

        category_status.append({
            "id": budget.id,
            "category": budget.category,
            "budget": budget_amount,
            "spent": spent,
            "remaining": round(budget_amount - spent, 2),
            "percent_used": round(percent_used, 1),
        })

    categories = list(set(
        [e.category for e in user_expenses] +
        [b.category for b in budgets]
    ))

    return render_template(
        "expenses.html",
        expenses=user_expenses,
        budgets=budgets,
        category_status=category_status,
        categories=get_categories(),
        currency_symbol=currency_symbol,
        user_settings=user_settings,
        next_reset_date=next_reset_date
    )

@expenses_bp.route('/reset_budget', methods=['POST'])
@login_required
def reset_budget():
    reset_date_str = request.form.get('reset_date')
    reset_date = datetime.strptime(reset_date_str, '%Y-%m-%d')
    
    # Find user settings and update the reset date
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if user_settings:
        user_settings.last_reset_at = reset_date
        db.session.commit()  # Commit the change to the database

    flash(f'Budget reset for {reset_date.strftime("%B %d, %Y")}.', 'success')
    return redirect(url_for('settings.settings'))


@expenses_bp.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date_str = request.form["date"]
        date = datetime.strptime(date_str, "%Y-%m-%d")
        expense = Expense(amount=amount, category=category, description=description, user_id=current_user.id, date=date)
        db.session.add(expense)
        db.session.commit()
        flash("Expense added successfully!")
        return redirect(url_for("expenses.expenses"))
    return render_template("add_expense.html", categories=get_categories())

@expenses_bp.route("/expenses/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        abort(403)
    if request.method == "POST":
        expense.amount = request.form["amount"]
        expense.category = request.form["category"]
        expense.description = request.form["description"]
        date_str = request.form["date"]
        expense.date = datetime.strptime(date_str, "%Y-%m-%d")
        db.session.commit()
        flash("Expense updated successfully!", "success")
        return redirect(url_for("expenses.expenses"))
    return render_template("edit_expense.html", expense=expense, categories=get_categories())

@expenses_bp.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash("You are not authorized to delete this expense.", "danger")
        return redirect(url_for("expenses.expenses"))
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully", "success")
    return redirect(url_for("expenses.expenses"))

@expenses_bp.route("/manage_budget", methods=["POST"])
@login_required
def manage_budget():
    category = request.form["category"]
    budget = float(request.form["budget"])

    existing_budget = Budget.query.filter_by(user_id=current_user.id, category=category).first()

    if existing_budget:
        existing_budget.amount = budget
    else:
        new_budget = Budget(
            amount=budget,
            category=category,
            user_id=current_user.id
        )
        db.session.add(new_budget)
    db.session.commit()

    return redirect(url_for("expenses.expenses"))

@expenses_bp.route("/delete_budget/<int:budget_id>", methods=["POST"])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash("You are not authorized to delete this budget.", "danger")
        return redirect(url_for("expenses.expenses"))
    db.session.delete(budget)
    db.session.commit()
    flash("Budget deleted successfully!", "success")
    return redirect(url_for("expenses.expenses"))