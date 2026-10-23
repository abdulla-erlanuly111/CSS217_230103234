import re
from abc import ABC, abstractmethod
from typing import List
from domain.models import Transaction

class BankImporterInterface(ABC):
    @abstractmethod
    def get_imported_transactions(self, user_id: int, category_id: int) -> List[Transaction]:
        pass

class ThirdPartyBankApiService:
    def fetch_statement(self, account_number: str) -> List[dict]:
        return [
            {"trx_ref": "EXT-9001", "val": -12500.0, "iso_date": "2026-10-15", "details": "Supermarket"},
            {"trx_ref": "EXT-9002", "val": 450000.0, "iso_date": "2026-10-16", "details": "Salary Payment"}
        ]

class BankApiAdapter(BankImporterInterface):
    def __init__(self, api_service: ThirdPartyBankApiService, account_number: str):
        self.api_service = api_service
        self.account_number = account_number.replace(" ", "").upper()
        self._validate_account_number()

    def _validate_account_number(self):
        pattern = r"^KZ\d{2}\d{3}[A-Z0-9]{13}$"
        if not re.match(pattern, self.account_number):
            raise ValueError(
                "Invalid account number format! Must comply with KZT IBAN standard (20 characters):\n"
                "- Country Code: 'KZ'\n"
                "- 2 Check Digits (e.g., '12')\n"
                "- 3 Bank Code Digits (e.g., Kaspi — 722, Halyk — 601, BCC — 856)\n"
                "- 13 Account Digits\n"
                "Example: KZ127221234567890123"
            )

    def get_imported_transactions(self, user_id: int, category_id: int) -> List[Transaction]:
        raw_data = self.api_service.fetch_statement(self.account_number)
        transactions = []
        for item in raw_data:
            raw_amount = item.get("val", 0.0)
            amount = abs(raw_amount)
            trx_type = "EXPENSE" if raw_amount < 0 else "INCOME"
            date = item.get("iso_date", "")
            description = f"[BankImport {item.get('trx_ref')}] {item.get('details')}"
            
            transactions.append(
                Transaction(
                    id=None,
                    user_id=user_id,
                    category_id=category_id,
                    amount=amount,
                    type=trx_type,
                    date=date,
                    description=description,
                    currency="KZT"
                )
            )
        return transactions
