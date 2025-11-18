from datetime import datetime
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    @app.route("/")
    def index():
        # For now, send some fake summary numbers.
        fake_summary = {
            "month": datetime.now().strftime("%B %Y"),
            "total_spent": 1243.78,
            "top_category": "Food & Coffee",
            "top_category_amount": 456.32,
            "transactions_count": 23
        }
        return render_template("index.html", summary=fake_summary)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)