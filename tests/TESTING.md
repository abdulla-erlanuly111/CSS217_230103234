# Test Suite Documentation

**Execution Command:** `pytest -v`  
**Test File Location:** `tests/test_all.py`  
**Total Test Cases:** 8 (3 Pattern Verification Tests + 5 Main Functionality Tests)  

| Test ID | Module / Focus | Test Case Name | Input Data | Expected Result | Status |
|---|---|---|---|---|---|
| **TC-01** | **Strategy Pattern** | `test_strategy_pattern_export` | Transaction data, `CsvExportStrategy`, `JsonExportStrategy` | Generates files in `reports/` and verifies physical file existence. | **PASSED** |
| **TC-02** | **Adapter Pattern** | `test_adapter_pattern_import` | Valid KZT IBAN `KZ127221234567890123` | Adapts raw external bank statement to 2 domain `Transaction` objects. | **PASSED** |
| **TC-03** | **Decorator Pattern** | `test_decorator_pattern_chain` | Overbudget message | Executes `BasicConsole` $\to$ `SMS` $\to$ `Email` $\to$ `HighPriority` chained alerts. | **PASSED** |
| **TC-04** | **Transaction Module** | `test_add_transaction_success` | Amount: 500.0 KZT, Date: `2026-10-23`, Description: "Groceries" | Transaction saved in SQLite with generated ID and currency KZT. | **PASSED** |
| **TC-05** | **Transaction Module** | `test_add_transaction_invalid_amount` | Amount: -50.0 KZT | Raises `ValueError` ("Transaction amount must be strictly positive"). | **PASSED** |
| **TC-06** | **Transaction Module** | `test_delete_transaction_success` | Existing Transaction ID | Deletes record from SQLite database and returns `True`. | **PASSED** |
| **TC-07** | **Category Module** | `test_add_category_success` | Name: "Salary", Type: "INCOME" | Category created and retrieved from SQLite repository. | **PASSED** |
| **TC-08** | **Budget Module** | `test_budget_exceeded_calculation` | Limit: 200.0 KZT, Expenses: 150.0 + 100.0 KZT | Accurately calculates total monthly spent as 250.0 KZT (> 200 limit). | **PASSED** |
