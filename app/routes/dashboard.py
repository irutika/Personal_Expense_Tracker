from flask import Blueprint, render_template, Response, request, jsonify
from flask_login import login_required, current_user
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from calendar import monthrange
from app.models import db, Expense, UserSettings

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@dashboard_bp.route('/spending_chart')
@login_required
def spending_chart():
    mode = request.args.get('mode', 'weekly')
    now = datetime.now()

    # Set date range and initialize totals
    if mode == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = monthrange(now.year, now.month)[1]
        end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        labels = list(map(str, range(1, last_day + 1)))
        totals = {day: 0 for day in range(1, last_day + 1)}

    # elif mode == 'yearly':
    #     start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    #     end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    #     labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
    #               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    #     totals = {month: 0 for month in range(1, 13)}

    else:  # weekly
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (start_date + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        totals = {i: 0 for i in range(7)}  # 0 = Mon, ..., 6 = Sun

    # Query expenses
    expenses = Expense.query.filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()

    # Aggregate amounts
    for expense in expenses:
        if mode == 'monthly':
            key = expense.date.day
        # elif mode == 'yearly':
        #     key = expense.date.month
        else:
            key = expense.date.weekday()
        totals[key] += float(expense.amount)

    # Format amounts for plotting
    if mode == 'monthly':
        amounts = [totals[day] for day in range(1, last_day + 1)]
        plot_labels = labels

    # elif mode == 'yearly':
    #     amounts = [totals[month] for month in range(1, 13)]
    #     plot_labels = labels

    else:  # weekly
        amounts = [totals[i] for i in range(7)]
        plot_labels = labels

    # Load user currency setting
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    currency = settings.preferred_currency if settings and settings.preferred_currency else "₹"

    # Plot generation

    fig, ax = plt.subplots(figsize=(12, 5))


    if all(amount == 0 for amount in amounts):
        ax.text(0.5, 0.5, "No spending data for this period",
                ha='center', va='center', fontsize=14, color='gray', transform=ax.transAxes)
        ax.axis('off')
    else:
        if mode == 'yearly':
            bars = ax.barh(plot_labels, amounts, color='lightgreen')
            ax.set_xlabel(f"Amount ({currency})")
            for bar, value in zip(bars, amounts):
                ax.text(value + 5, bar.get_y() + bar.get_height()/2,
                        f"{currency}{value:.2f}", va='center', fontsize=8)
        else:
            bars = ax.bar(plot_labels, amounts, color='lightgreen')
            ax.set_ylabel(f"Amount ({currency})")
            if mode == 'monthly':
                plt.xticks(rotation=60, ha='right', fontsize=8)
            else:
                plt.xticks(rotation=0, fontsize=10)

            for bar, value in zip(bars, amounts):
                ax.text(bar.get_x() + bar.get_width()/2, value + 5,
                        f"{currency}{value:.2f}", ha='center', va='bottom', fontsize=8)

        ax.set_title("Spending Trends", fontsize=16, loc='left')
        ax.set_ylim(0, max(amounts) * 1.2)
        ax.grid(axis='y', linestyle='--', linewidth=0.5)

    # Return plot as image
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return Response(img.getvalue(), mimetype='image/png')
