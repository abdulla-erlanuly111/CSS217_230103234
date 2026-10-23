**Course:** CSS217 — Assignment 2  
**Language:** Python 3.10+  
**Currency:** Kazakhstani Tenge (KZT)  
**Database:** SQLite (`finance.db`)  
**User Interface:** Streamlit + Plotly  

---

## 📌 Project Overview

An N-Tier Personal Finance and Expense Management Web Application built in Python. The system allows users to track income and expenses in **KZT**, manage category budgets, visualize spending through interactive charts, import bank statements, and export financial reports in multiple formats.

### Core Features:
1. **Transaction Management:** Add, view, and delete income/expense transactions linked to categories.
2. **Interactive Analytics:** Dashboard displaying total income, total expenses, net balance, and an interactive **Plotly Donut Chart** showing expense distribution by category.
3. **Category Management:** Create new categories and safely delete existing ones (with foreign key relationship protection).
4. **Monthly Budgeting:** Set monthly expense limits per category.
5. **Bank Import (Adapter Pattern):** Import external bank API statements with validation for Kazakhstani IBAN account numbers.
6. **Report Export (Strategy Pattern):** Export transaction reports into CSV, JSON, or TXT formats saved inside the `reports/` folder.
7. **Overbudget Notifications (Decorator Pattern):** Layered notification chain triggering alerts when monthly budget limits are exceeded.

---

## 🏛️ System Architecture (N-Tier)

The application follows strict N-Tier architectural principles:

* **`domain/` (Domain Layer):** Contains core data models (`User`, `Category`, `Transaction`, `Budget`).
* **`dal/` (Data Access Layer):** Handles database connections (`Database`) and CRUD repositories (`UserRepository`, `CategoryRepository`, `TransactionRepository`, `BudgetRepository`).
* **`bll/` (Business Logic Layer):** Houses core services (`FinanceService`), design pattern implementations, strict input validation, and budget monitoring.
* **`presentation/` (Presentation Layer):** Streamlit web user interface (`app.py`) with vertical radio navigation.

```text
Assignment2_CSS217/
├── domain/               # Domain Entity Data Classes
│   └── models.py
├── dal/                  # Data Access Layer (SQLite & Repositories)
│   ├── database.py
│   └── repositories.py
├── bll/                  # Business Logic Layer & Design Patterns
│   ├── services.py
│   ├── strategies.py     # Strategy Pattern
│   ├── adapters.py       # Adapter Pattern
│   └── decorators.py     # Decorator Pattern
├── presentation/         # Presentation Layer (Streamlit App)
│   └── app.py
├── reports/              # Exported Report Files
├── tests/                # Automated Test Suite (Pytest)
│   └── test_all.py
├── finance.db            # Persistent SQLite Database
├── requirements.txt      # Project Dependencies
└── README.md             # Project Documentation