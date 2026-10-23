import unittest
import os
from dal.database import Database
from dal.repositories import UserRepository, CategoryRepository, TransactionRepository, BudgetRepository
from bll.services import FinanceService
from bll.strategies import CsvExportStrategy, JsonExportStrategy, TxtExportStrategy
from bll.adapters import ThirdPartyBankApiService, BankApiAdapter
from bll.decorators import BasicConsoleNotifier, EmailNotificationDecorator, SmsNotificationDecorator, HighPriorityAlertDecorator
from domain.models import User

class TestFinanceApp(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_finance.db"
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

        self.db = Database(self.db_path)
        self.user_repo = UserRepository(self.db)
        self.cat_repo = CategoryRepository(self.db)
        self.trx_repo = TransactionRepository(self.db)
        self.budget_repo = BudgetRepository(self.db)
        self.service = FinanceService(user_repo=self.user_repo, cat_repo=self.cat_repo, trx_repo=self.trx_repo, budget_repo=self.budget_repo)
        
        self.user = self.user_repo.add(User(id=None, username="tester", email="test@test.com"))
        self.cat = self.service.add_category("Food", "EXPENSE")

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    # === PATTERN TESTS (3) ===
    def test_strategy_pattern_export(self):
        self.service.add_transaction(self.user.id, self.cat.id, 100.0, "EXPENSE", "2026-10-20", "Lunch")
        csv_file = self.service.export_report(self.user.id, CsvExportStrategy(), "test_report")
        json_file = self.service.export_report(self.user.id, JsonExportStrategy(), "test_report")
        
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.exists(json_file))
        if os.path.exists(csv_file):
            os.remove(csv_file)
        if os.path.exists(json_file):
            os.remove(json_file)

    def test_adapter_pattern_import(self):
        bank_service = ThirdPartyBankApiService()
        adapter = BankApiAdapter(bank_service, "KZ127221234567890123")
        count = self.service.import_external_transactions(self.user.id, adapter, self.cat.id)
        self.assertEqual(count, 2)

    def test_decorator_pattern_chain(self):
        notifier = HighPriorityAlertDecorator(EmailNotificationDecorator(SmsNotificationDecorator(BasicConsoleNotifier())))
        result = notifier.send("Overbudget Test Alert")
        self.assertIn("🚨 HIGH PRIORITY OVERBUDGET", result)
        self.assertIn("[EMAIL ALERT SENT]", result)
        self.assertIn("[SMS ALERT SENT]", result)

    # === MAIN FUNCTIONALITY TESTS (5) ===
    def test_add_transaction_success(self):
        trx = self.service.add_transaction(self.user.id, self.cat.id, 500.0, "EXPENSE", "2026-10-23", "Groceries")
        self.assertIsNotNone(trx.id)
        self.assertEqual(trx.amount, 500.0)
        self.assertEqual(trx.currency, "KZT")

    def test_add_transaction_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.service.add_transaction(self.user.id, self.cat.id, -50.0, "EXPENSE", "2026-10-23", "Invalid")

    def test_delete_transaction_success(self):
        trx = self.service.add_transaction(self.user.id, self.cat.id, 300.0, "EXPENSE", "2026-10-23", "To Delete")
        deleted = self.service.delete_transaction(trx.id)
        self.assertTrue(deleted)
        remaining = self.trx_repo.get_by_user(self.user.id)
        self.assertEqual(len(remaining), 0)

    def test_add_category_success(self):
        cat = self.service.add_category("Salary", "INCOME")
        self.assertIsNotNone(cat.id)
        self.assertEqual(cat.name, "Salary")
        self.assertEqual(cat.type, "INCOME")

    def test_budget_exceeded_calculation(self):
        self.service.set_budget(self.user.id, self.cat.id, 200.0, "2026-10")
        self.service.add_transaction(self.user.id, self.cat.id, 150.0, "EXPENSE", "2026-10-10", "Item 1")
        self.service.add_transaction(self.user.id, self.cat.id, 100.0, "EXPENSE", "2026-10-12", "Item 2")
        spent = self.trx_repo.get_spent_by_category_and_month(self.user.id, self.cat.id, "2026-10")
        self.assertEqual(spent, 250.0)

if __name__ == "__main__":
    unittest.main()
