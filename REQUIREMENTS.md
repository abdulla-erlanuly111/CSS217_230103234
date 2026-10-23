# 📋 Software Requirements Specification (SRS)

**Project Title:** Personal Finance and Expense Management System  
**Course:** CSS217 — Assignment 2  
**Target Currency:** Kazakhstani Tenge (KZT)  

## 1. System Scope & Purpose
The Personal Finance System provides individual users with persistent tracking of income and expenses, monthly budget enforcement, automated third-party bank statement imports, and multi-format report generation. The system is designed following strict N-Tier architectural principles and design patterns.

## 2. Functional Requirements (FR)

| ID | Module | Description | Validation / Constraints |
|---|---|---|---|
| **FR-01** | **Category Management** | Create and view income/expense categories. Allow deletion only if unlinked to active transactions/budgets. | Category name cannot be empty. Type must be 'INCOME' or 'EXPENSE'. |
| **FR-02** | **Transaction Tracking** | Record, view, and delete income/expense transactions linked to categories. | Amount must be > 0 KZT. Description cannot be empty. |
| **FR-03** | **Budgeting & Alerts** | Set monthly spending limits per category. Automatically trigger notifications when limits are exceeded. | Month format: `YYYY-MM`. Limit > 0 KZT. Triggers Decorator pattern chain. |
| **FR-04** | **Bank Statement Import** | Import external bank statements via an adapter layer. | Validates 20-character KZT IBAN (`^KZ\d{2}\d{3}[A-Z0-9]{13}$`). |
| **FR-05** | **Report Export** | Export transaction history to CSV, JSON, or TXT formats saved to `reports/`. | Filename cannot be empty. Uses Strategy pattern. |
| **FR-06** | **Analytics Dashboard** | Display total income, total expense, net balance, and an interactive Plotly donut chart. | Grouped by expense categories. |

## 3. Non-Functional Requirements (NFR)

* **NFR-01 (Architecture):** Must adhere to a 4-tier architecture (`domain`, `dal`, `bll`, `presentation`).
* **NFR-02 (Data Persistence):** All data must persist in SQLite (`finance.db`) across application restarts.
* **NFR-03 (Input Validation & Error Handling):** All empty or malformed inputs must raise explicit error messages.
* **NFR-04 (Maintainability & Design Patterns):** Must implement Strategy, Adapter, and Decorator design patterns in working code.
* **NFR-05 (Testability):** Must achieve 100% pass rate across at least 8 unit tests in `pytest`.
