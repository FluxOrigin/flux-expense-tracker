"""
Flux Expense Tracker

A small, portfolio-focused Flask application for tracking personal expenses
with a modern UI and a Chart.js-powered dashboard.

Author: FluxOrigin
"""

__version__ = "1.0.0"


from datetime import datetime, date
from collections import defaultdict
from calendar import month_name

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy


# Global SQLAlchemy object
db = SQLAlchemy()

    # -------------------- MODELS -------------------- #
    
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    expenses = db.relationship("Expense", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name!r}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.Date, nullable=False, default=date.today)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", back_populates="expenses")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Expense {self.amount} {self.category.name} {self.date}>"

    # -------------------- QUERY HELPERS -------------------- #

def get_month_expenses(year: int, month: int):
    """
    Return all expenses for a given year/month, ordered by date ascending.
    """
    first = date(year, month, 1)
    # compute first day of next month
    if month == 12:
        next_first = date(year + 1, 1, 1)
    else:
        next_first = date(year, month + 1, 1)

    return (
        Expense.query
        .filter(Expense.date >= first, Expense.date < next_first)
        .order_by(Expense.date.asc())
        .all()
    )


def get_current_month_expenses():
    """
    Convenience wrapper for the current month.
    """
    today = date.today()
    return get_month_expenses(today.year, today.month)

    # -------------------- APPLICATION FACTORY -------------------- #

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # -------------------- ROUTES -------------------- #

    @app.route("/")
    def index():
        """
        Dashboard. Shows summary for the selected month (default = current).
        """
        today = date.today()

        # Read filters from query string; fall back to current month/year
        selected_year = request.args.get("year", type=int) or today.year
        selected_month = request.args.get("month", type=int) or today.month

        monthly_expenses = get_month_expenses(selected_year, selected_month)

        total_spent = sum(float(e.amount) for e in monthly_expenses)
        per_category = defaultdict(float)

        for e in monthly_expenses:
            per_category[e.category.name] += float(e.amount)

        if per_category:
            top_category_name = max(per_category, key=per_category.get)
            top_category_amount = per_category[top_category_name]
        else:
            top_category_name = "N/A"
            top_category_amount = 0.0

        month_label = f"{month_name[selected_month]} {selected_year}"

        summary = {
            "month": month_label,
            "total_spent": total_spent,
            "top_category": top_category_name,
            "top_category_amount": top_category_amount,
            "transactions_count": len(monthly_expenses),
        }

        # Month options: always all 12
        month_options = [(i, month_name[i]) for i in range(1, 13)]

        # Year options: based on actual data in the database
        min_date = db.session.query(db.func.min(Expense.date)).scalar()
        max_date = db.session.query(db.func.max(Expense.date)).scalar()

        if min_date and max_date:
            year_options = list(range(min_date.year, max_date.year + 1))
        else:
            # If no expenses yet, just show the current year
            year_options = [today.year]

        return render_template(
            "index.html",
            summary=summary,
            active_page="dashboard",
            month_options=month_options,
            year_options=year_options,
            selected_month=selected_month,
            selected_year=selected_year,
        )

    @app.route("/api/monthly-category-breakdown")
    def monthly_category_breakdown():
        """
        Return JSON with spending per category for the selected month/year.
        Defaults to current month/year if not provided.
        """
        today = date.today()
        year_arg = request.args.get("year", type=int) or today.year
        month_arg = request.args.get("month", type=int) or today.month

        expenses = get_month_expenses(year_arg, month_arg)
        per_category = defaultdict(float)

        for e in expenses:
            per_category[e.category.name] += float(e.amount)

        labels = list(per_category.keys())
        values = [round(per_category[name], 2) for name in labels]

        return jsonify({"labels": labels, "values": values})

    @app.route("/expenses", methods=["GET"])
    def expenses():
        """
        List all recorded expenses, newest first.
        """
        all_expenses = (
            Expense.query
            .order_by(Expense.date.desc(), Expense.created_at.desc())
            .all()
        )
        return render_template(
            "expenses.html",
            expenses=all_expenses,
            active_page="expenses",
        )

    @app.route("/expenses/new", methods=["GET", "POST"])
    def new_expense():
        """
        Create a new expense via a simple HTML form.
        """
        if request.method == "POST":
            amount_raw = request.form.get("amount", "").strip()
            date_raw = request.form.get("date", "").strip()
            category_name = request.form.get("category", "").strip()
            new_category_name = request.form.get("new_category", "").strip()
            description = request.form.get("description", "").strip()

            # Basic validation
            if not amount_raw or not date_raw:
                flash("Amount and date are required.", "error")
                return redirect(url_for("new_expense"))

            try:
                amount = float(amount_raw)
            except ValueError:
                flash("Amount must be a valid number.", "error")
                return redirect(url_for("new_expense"))

            try:
                expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "error")
                return redirect(url_for("new_expense"))

            # Decide which category to use
            if new_category_name:
                category = get_or_create_category(new_category_name)
            elif category_name:
                category = get_or_create_category(category_name)
            else:
                category = get_or_create_category("Uncategorized")

            expense = Expense(
                amount=amount,
                description=description,
                date=expense_date,
                category=category,
            )

            db.session.add(expense)
            db.session.commit()

            flash("Expense added.", "success")
            return redirect(url_for("expenses"))

        # GET request → show the form with existing categories
        categories = Category.query.order_by(Category.name).all()
        return render_template(
            "new_expense.html",
            categories=categories,
            active_page="expenses",
        )

    @app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
    def edit_expense(expense_id: int):
        """
        Edit an existing expense.
        """
        expense = Expense.query.get_or_404(expense_id)

        if request.method == "POST":
            amount_raw = request.form.get("amount", "").strip()
            date_raw = request.form.get("date", "").strip()
            category_name = request.form.get("category", "").strip()
            new_category_name = request.form.get("new_category", "").strip()
            description = request.form.get("description", "").strip()

            if not amount_raw or not date_raw:
                flash("Amount and date are required.", "error")
                return redirect(url_for("edit_expense", expense_id=expense.id))

            try:
                amount = float(amount_raw)
            except ValueError:
                flash("Amount must be a valid number.", "error")
                return redirect(url_for("edit_expense", expense_id=expense.id))

            try:
                expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "error")
                return redirect(url_for("edit_expense", expense_id=expense.id))

            # Decide which category to use
            if new_category_name:
                category = get_or_create_category(new_category_name)
            elif category_name:
                category = get_or_create_category(category_name)
            else:
                category = get_or_create_category("Uncategorized")

            # Apply updates
            expense.amount = amount
            expense.date = expense_date
            expense.description = description
            expense.category = category

            db.session.commit()

            flash("Expense updated.", "success")
            return redirect(url_for("expenses"))

        # GET → show form pre-filled
        categories = Category.query.order_by(Category.name).all()
        return render_template(
            "edit_expense.html",
            expense=expense,
            categories=categories,
            active_page="expenses",
        )

    @app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
    def delete_expense(expense_id: int):
        """
        Delete an existing expense.
        """
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted.", "success")
        return redirect(url_for("expenses"))

    @app.route("/init-db")
    def init_db_route():
        """
        Convenience route to create the database and seed a few example records.
        Not for production; just to bootstrap the demo locally.
        """
        with app.app_context():
            db.drop_all()
            db.create_all()
            seed_example_data()
        return "Database initialized with example data."

    return app


def seed_example_data():
    """
    Insert a few example categories and expenses to make the dashboard look alive.
    """
    categories = [
        Category(name="Food & Coffee"),
        Category(name="Rent"),
        Category(name="Subscriptions"),
        Category(name="Transport"),
        Category(name="Health & Fitness"),
    ]

    for c in categories:
        db.session.add(c)
    db.session.commit()

    # Helper to fetch category by name quickly
    def get_cat(name):
        return Category.query.filter_by(name=name).first()

    today = date.today()
    sample_expenses = [
        Expense(
            amount=18.50,
            description="Coffee + breakfast",
            date=today,
            category=get_cat("Food & Coffee"),
        ),
        Expense(
            amount=9.99,
            description="Streaming subscription",
            date=today.replace(day=max(1, today.day - 2)),
            category=get_cat("Subscriptions"),
        ),
        Expense(
            amount=1250.00,
            description="Monthly rent",
            date=today.replace(day=1),
            category=get_cat("Rent"),
        ),
        Expense(
            amount=42.30,
            description="Gas + tolls",
            date=today.replace(day=max(1, today.day - 3)),
            category=get_cat("Transport"),
        ),
        Expense(
            amount=29.00,
            description="Gym membership",
            date=today.replace(day=max(1, today.day - 5)),
            category=get_cat("Health & Fitness"),
        ),
    ]

    for e in sample_expenses:
        db.session.add(e)

    db.session.commit()


def get_or_create_category(name: str) -> Category:
    """
    Fetch a category by name, creating it if it does not exist.
    """
    name = (name or "").strip()
    if not name:
        name = "Uncategorized"

    category = Category.query.filter_by(name=name).first()
    if category is None:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
    return category


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)