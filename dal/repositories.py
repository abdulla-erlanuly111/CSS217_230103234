from typing import List, Optional
from domain.models import User, Category, Transaction, Budget
from dal.database import Database

class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, user: User) -> User:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, role) VALUES (?, ?, ?)",
                (user.username, user.email, user.role)
            )
            user.id = cursor.lastrowid
            conn.commit()
            return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if row:
                return User(id=row['id'], username=row['username'], email=row['email'], role=row['role'])
            return None

class CategoryRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, category: Category) -> Category:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, type) VALUES (?, ?)",
                (category.name, category.type)
            )
            category.id = cursor.lastrowid
            conn.commit()
            return category

    def delete(self, category_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all(self) -> List[Category]:
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM categories").fetchall()
            return [Category(id=r['id'], name=r['name'], type=r['type']) for r in rows]

    def get_by_id(self, category_id: int) -> Optional[Category]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
            if row:
                return Category(id=row['id'], name=row['name'], type=row['type'])
            return None

    def get_by_name(self, name: str) -> Optional[Category]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM categories WHERE name = ?", (name,)).fetchone()
            if row:
                return Category(id=row['id'], name=row['name'], type=row['type'])
            return None

class TransactionRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, transaction: Transaction) -> Transaction:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transactions (user_id, category_id, amount, type, date, description, currency) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (transaction.user_id, transaction.category_id, transaction.amount, transaction.type, transaction.date, transaction.description, transaction.currency)
            )
            transaction.id = cursor.lastrowid
            conn.commit()
            return transaction

    def delete(self, transaction_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_by_user(self, user_id: int) -> List[Transaction]:
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()
            return [Transaction(id=r['id'], user_id=r['user_id'], category_id=r['category_id'],
                                amount=r['amount'], type=r['type'], date=r['date'], description=r['description'],
                                currency=r['currency'] if 'currency' in r.keys() else 'KZT') for r in rows]

    def get_spent_by_category_and_month(self, user_id: int, category_id: int, month_year: str) -> float:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT SUM(amount) as total FROM transactions WHERE user_id = ? AND category_id = ? AND date LIKE ? AND type = 'EXPENSE'",
                (user_id, category_id, f"{month_year}%")
            ).fetchone()
            return row['total'] if row and row['total'] else 0.0

class BudgetRepository:
    def __init__(self, db: Database):
        self.db = db

    def set_budget(self, budget: Budget) -> Budget:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO budgets (user_id, category_id, monthly_limit, month_year, currency) VALUES (?, ?, ?, ?, ?)",
                (budget.user_id, budget.category_id, budget.monthly_limit, budget.month_year, budget.currency)
            )
            budget.id = cursor.lastrowid
            conn.commit()
            return budget

    def get_budget(self, user_id: int, category_id: int, month_year: str) -> Optional[Budget]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM budgets WHERE user_id = ? AND category_id = ? AND month_year = ?",
                (user_id, category_id, month_year)
            ).fetchone()
            if row:
                return Budget(id=row['id'], user_id=row['user_id'], category_id=row['category_id'],
                              monthly_limit=row['monthly_limit'], month_year=row['month_year'],
                              currency=row['currency'] if 'currency' in row.keys() else 'KZT')
            return None
