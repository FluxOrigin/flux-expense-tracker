# Flux Expense Tracker

A clean, modern personal expense tracker built with **Flask**, **SQLite**, and a **Chart.js**-powered dashboard.  
This project is designed as a portfolio-ready example of a small but well-structured full-stack application.

> Track where your money goes, visualize it by category, and explore your history with a simple month/year filter.

---

## Features

- **Dashboard Overview**
  - Total spending for the selected month
  - Top spending category + amount
  - Number of transactions in the selected period
  - Month/year filter that dynamically updates both the summary and the chart

- **Expense Management (CRUD)**
  - Add new expenses with:
    - Amount
    - Date
    - Category (select existing or create a new one on the fly)
    - Optional description/notes
  - View all expenses in a clean, scrollable table
  - Edit existing expenses
  - Delete expenses with confirmation

- **Visual Analytics**
  - Donut chart showing spending by category for the selected month
  - Powered by a small JSON API endpoint and Chart.js
  - Auto-updates based on selected month/year

- **Smart Filters**
  - Year dropdown is generated based on the actual data range in the database  
    (from the earliest to the latest expense year)
  - Month dropdown always covers all 12 months

- **Nice UI / UX**
  - Dark, glassy layout with accent gradients
  - Responsive sidebar and content area
  - Button styles for primary, secondary, and destructive actions
  - Flash messages for success/error states

---

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite (file-based, via SQLAlchemy ORM)
- **Frontend:** HTML, Jinja2 templates, CSS
- **Charts:** Chart.js (via CDN)

---

## Why this project exists

This app is intentionally small but complete: it’s designed to show how I think about
data modeling, UX, and clean separation of concerns in a full-stack context.

I wanted something more realistic than a toy “to-do list,” but still light enough
to read and understand in one sitting. It demonstrates:

- A simple, expressive schema (Expenses + Categories)
- Server-side rendering with modern styling
- A small JSON API powering a Chart.js visualization
- Basic product thinking around filters, summaries, and workflows

---

## Project Structure

```text
flux-expense-tracker/
│
├── app.py                  # Main Flask application and routes
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignore virtualenv, DB files, etc.
│
├── templates/
│   ├── base.html           # Base layout (sidebar, header, footer)
│   ├── index.html          # Dashboard with filters and chart
│   ├── expenses.html       # Expense list table + actions
│   ├── new_expense.html    # Create expense form
│   └── edit_expense.html   # Edit expense form
│
└── static/
    ├── css/
    │   └── style.css       # Custom styling, layout, and theming
    └── js/
        └── main.js         # Chart.js integration and dashboard logic

---

## License ##

This project is licensed under the **MIT License**.  
See the [`LICENSE`](./LICENSE) file for details.