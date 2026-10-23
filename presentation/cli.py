import sys
from dal.database import Database
from dal.repositories import UserRepository, CategoryRepository, TransactionRepository, BudgetRepository
from bll.services import FinanceService
from bll.strategies import CsvExportStrategy, JsonExportStrategy, TxtExportStrategy
from bll.adapters import ThirdPartyBankApiService, BankApiAdapter
from domain.models import User

class FinanceCLI:
    def __init__(self):
        self.db = Database("finance.db")
        self.user_repo = UserRepository(self.db)
        self.cat_repo = CategoryRepository(self.db)
        self.trx_repo = TransactionRepository(self.db)
        self.budget_repo = BudgetRepository(self.db)
        self.service = FinanceService(self.user_repo, self.cat_repo, self.trx_repo, self.budget_repo)
        self.current_user = None

    def setup_default_data(self):
        user = self.user_repo.get_by_id(1)
        if not user:
            user = self.user_repo.add(User(id=None, username="default_user", email="user@example.com"))
        self.current_user = user

        if not self.cat_repo.get_all():
            self.service.add_category("Salary", "INCOME")
            self.service.add_category("Groceries", "EXPENSE")
            self.service.add_category("Bank Import", "EXPENSE")

    def run(self):
        self.setup_default_data()
        print("=== PERSONAL FINANCE SYSTEM ===")
        while True:
            print("\n1. Add Transaction")
            print("2. Add Category")
            print("3. Set Monthly Budget")
            print("4. Export Report (Strategy Pattern)")
            print("5. Import Bank Transactions (Adapter Pattern)")
            print("6. View Transactions")
            print("0. Exit")
            choice = input("Select option: ").strip()

            try:
                if choice == "1":
                    self.ui_add_transaction()
                elif choice == "2":
                    self.ui_add_category()
                elif choice == "3":
                    self.ui_set_budget()
                elif choice == "4":
                    self.ui_export_report()
                elif choice == "5":
                    self.ui_import_bank()
                elif choice == "6":
                    self.ui_view_transactions()
                elif choice == "0":
                    print("Goodbye!")
                    sys.exit(0)
                else:
                    print("Invalid choice!")
            except Exception as e:
                print(f"Error: {e}")

    def ui_add_transaction(self):
        cats = self.cat_repo.get_all()
        print("\nCategories:")
        for c in cats:
            print(f"ID: {c.id} | {c.name} ({c.type})")
        
        cat_id = int(input("Category ID: "))
        amount = float(input("Amount: "))
        trx_type = input("Type (INCOME/EXPENSE): ").upper()
        date = input("Date (YYYY-MM-DD): ")
        desc = input("Description: ")
        
        self.service.add_transaction(self.current_user.id, cat_id, amount, trx_type, date, desc)
        print("Transaction added successfully!")

    def ui_add_category(self):
        name = input("Category Name: ")
        cat_type = input("Type (INCOME/EXPENSE): ").upper()
        self.service.add_category(name, cat_type)
        print("Category added!")

    def ui_set_budget(self):
        cat_id = int(input("Expense Category ID: "))
        limit = float(input("Monthly Limit: "))
        month_year = input("Month (YYYY-MM): ")
        self.service.set_budget(self.current_user.id, cat_id, limit, month_year)
        print("Budget updated!")

    def ui_export_report(self):
        print("\nSelect Format:")
        print("1. CSV")
        print("2. JSON")
        print("3. TXT")
        fmt = input("Choice: ")
        filename = input("Filename (without extension): ")

        if fmt == "1":
            strat = CsvExportStrategy()
        elif fmt == "2":
            strat = JsonExportStrategy()
        elif fmt == "3":
            strat = TxtExportStrategy()
        else:
            print("Invalid format!")
            return

        res = self.service.export_report(self.current_user.id, strat, filename)
        print(f"Report exported to {res}")

    def ui_import_bank(self):
        bank_service = ThirdPartyBankApiService()
        adapter = BankApiAdapter(bank_service, "KZ99887766")
        default_cat = self.cat_repo.get_by_name("Bank Import")
        count = self.service.import_external_transactions(self.current_user.id, adapter, default_cat.id)
        print(f"Successfully imported {count} transactions from external bank!")

    def ui_view_transactions(self):
        trxs = self.trx_repo.get_by_user(self.current_user.id)
        print("\n=== TRANSACTION HISTORY ===")
        for t in trxs:
            cat = self.cat_repo.get_by_id(t.category_id)
            print(f"[{t.date}] {t.type} | Amount: {t.amount} | Cat: {cat.name if cat else 'N/A'} | Desc: {t.description}")
