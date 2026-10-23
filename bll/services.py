from typing import List, Dict, Any, Optional
from domain.models import Transaction, Category, Budget, User
from dal.repositories import UserRepository, CategoryRepository, TransactionRepository, BudgetRepository
from bll.strategies import ReportExporterContext, ReportExportStrategy
from bll.adapters import BankImporterInterface
from bll.decorators import Notifier, BasicConsoleNotifier, EmailNotificationDecorator, SmsNotificationDecorator, HighPriorityAlertDecorator

class FinanceService:
    def __init__(
        self,
        user_repo: UserRepository,
        cat_repo: CategoryRepository,
        trx_repo: TransactionRepository,
        budget_repo: BudgetRepository
    ):
        self.user_repo = user_repo
        self.cat_repo = cat_repo
        self.trx_repo = trx_repo
        self.budget_repo = budget_repo

    def add_category(self, name: str, cat_type: str) -> Category:
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty. Please enter a valid name.")
        if cat_type not in ["INCOME", "EXPENSE"]:
            raise ValueError("Category type must be 'INCOME' or 'EXPENSE'.")
        category = Category(id=None, name=name.strip(), type=cat_type)
        return self.cat_repo.add(category)

    def delete_category(self, category_id: int) -> bool:
        cat = self.cat_repo.get_by_id(category_id)
        if not cat:
            raise ValueError("Category not found.")

        with self.cat_repo.db.get_connection() as conn:
            trx_count = conn.execute("SELECT COUNT(*) as count FROM transactions WHERE category_id = ?", (category_id,)).fetchone()['count']
            budget_count = conn.execute("SELECT COUNT(*) as count FROM budgets WHERE category_id = ?", (category_id,)).fetchone()['count']
            if trx_count > 0 or budget_count > 0:
                raise ValueError("Cannot delete category: it is currently linked to active transactions or budgets.")

        return self.cat_repo.delete(category_id)

    def add_transaction(self, user_id: int, category_id: int, amount: float, trx_type: str, date: str, description: str, currency: str = "KZT") -> Transaction:
        if not description or not description.strip():
            raise ValueError("Description cannot be empty. Please enter a description.")
        if amount <= 0:
            raise ValueError("Transaction amount must be strictly positive.")
        if trx_type not in ["INCOME", "EXPENSE"]:
            raise ValueError("Transaction type must be 'INCOME' or 'EXPENSE'.")
        category = self.cat_repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found.")

        trx = Transaction(id=None, user_id=user_id, category_id=category_id, amount=amount, type=trx_type, date=date, description=description.strip(), currency=currency)
        saved_trx = self.trx_repo.add(trx)

        if trx_type == "EXPENSE":
            month_year = date[:7]
            self.check_budget_and_notify(user_id, category_id, month_year)

        return saved_trx

    def delete_transaction(self, transaction_id: int) -> bool:
        return self.trx_repo.delete(transaction_id)

    def set_budget(self, user_id: int, category_id: int, limit_amount: float, month_year: str, currency: str = "KZT") -> Budget:
        if limit_amount <= 0:
            raise ValueError("Budget limit must be strictly positive.")
        budget = Budget(id=None, user_id=user_id, category_id=category_id, monthly_limit=limit_amount, month_year=month_year, currency=currency)
        return self.budget_repo.set_budget(budget)

    def check_budget_and_notify(self, user_id: int, category_id: int, month_year: str):
        budget = self.budget_repo.get_budget(user_id, category_id, month_year)
        if not budget:
            return

        spent = self.trx_repo.get_spent_by_category_and_month(user_id, category_id, month_year)
        if spent > budget.monthly_limit:
            cat = self.cat_repo.get_by_id(category_id)
            cat_name = cat.name if cat else "Unknown"
            
            notifier_chain: Notifier = HighPriorityAlertDecorator(
                EmailNotificationDecorator(
                    SmsNotificationDecorator(BasicConsoleNotifier())
                )
            )
            notifier_chain.send(f"Exceeded limit for category '{cat_name}'! Spent: {spent:.2f} {budget.currency} / Limit: {budget.monthly_limit:.2f} {budget.currency}")

    def export_report(self, user_id: int, strategy: ReportExportStrategy, filename: str) -> str:
        if not filename or not filename.strip():
            raise ValueError("File name cannot be empty. Please enter a valid file name.")
        
        transactions = self.trx_repo.get_by_user(user_id)
        data = []
        for t in transactions:
            cat = self.cat_repo.get_by_id(t.category_id)
            data.append({
                "date": t.date,
                "type": t.type,
                "amount": t.amount,
                "currency": t.currency,
                "category": cat.name if cat else "N/A",
                "description": t.description
            })
        exporter = ReportExporterContext(strategy)
        return exporter.generate_report(data, filename.strip())

    def import_external_transactions(self, user_id: int, importer: BankImporterInterface, default_cat_id: int) -> int:
        imported_trxs = importer.get_imported_transactions(user_id, default_cat_id)
        count = 0
        for trx in imported_trxs:
            self.add_transaction(trx.user_id, trx.category_id, trx.amount, trx.type, trx.date, trx.description, trx.currency)
            count += 1
        return count
