from datetime import datetime, date
from collections import defaultdict

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy object (initialized with the app in create_app)
db = SQLAlchemy()


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


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.route("/")
    def index():
        """
        Dashboard. Shows summary for the current month, based on real DB data.
        """
        today = date.today()
        month_start = date(today.year, today.month, 1)

        # Get all expenses for the current month
        monthly_expenses = (
            Expense.query
            .filter(Expense.date >= month_start, Expense.date <= today)
            .order_by(Expense.date.desc())
            .all()
        )

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

        summary = {
            "month": today.strftime("%B %Y"),
            "total_spent": total_spent,
            "top_category": top_category_name,
            "top_category_amount": top_category_amount,
            "transactions_count": len(monthly_expenses),
        }

        return render_template("index.html", summary=summary)

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


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)