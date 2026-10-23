import os
import sys

# Fix import path for dal, bll, and domain modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
import streamlit as st
import plotly.graph_objects as go
from dal.database import Database
from dal.repositories import UserRepository, CategoryRepository, TransactionRepository, BudgetRepository
from bll.services import FinanceService
from bll.strategies import CsvExportStrategy, JsonExportStrategy, TxtExportStrategy
from bll.adapters import ThirdPartyBankApiService, BankApiAdapter
from domain.models import User

# Initialize Database and Services
@st.cache_resource
def get_service():
    db = Database("finance.db")
    user_repo = UserRepository(db)
    cat_repo = CategoryRepository(db)
    trx_repo = TransactionRepository(db)
    budget_repo = BudgetRepository(db)
    service = FinanceService(user_repo, cat_repo, trx_repo, budget_repo)

    # Default User
    user = user_repo.get_by_id(1)
    if not user:
        user = user_repo.add(User(id=None, username="default_user", email="user@example.com"))

    # Safely add default categories in English
    default_categories = [
        ("Salary", "INCOME"),
        ("Groceries", "EXPENSE"),
        ("Bank Import", "EXPENSE")
    ]
    for name, cat_type in default_categories:
        if not cat_repo.get_by_name(name):
            service.add_category(name, cat_type)

    return service, user

service, current_user = get_service()

st.set_page_config(page_title="Personal Finance Management", page_icon="💰", layout="wide")

st.sidebar.markdown("### 📌 Navigation")

nav_options = [
    "📊 Overview & Transactions",
    "➕ Add Transaction",
    "🏷️ Categories",
    "🎯 Budgets",
    "🔌 Bank Import (Adapter)",
    "📤 Export Report (Strategy)"
]

menu = st.sidebar.radio(
    label="Navigation",
    options=nav_options,
    label_visibility="collapsed"
)

st.title("💰 Personal Finance & Expense Management System")

# 1. OVERVIEW & TRANSACTIONS WITH DONUT CHART
if menu == "📊 Overview & Transactions":
    st.header("📊 Financial Overview")
    transactions = service.trx_repo.get_by_user(current_user.id)

    if transactions:
        expense_by_cat = {}
        total_income = 0.0
        total_expense = 0.0

        for t in transactions:
            cat = service.cat_repo.get_by_id(t.category_id)
            cat_name = cat.name if cat else "Uncategorized"
            if t.type == "EXPENSE":
                total_expense += t.amount
                expense_by_cat[cat_name] = expense_by_cat.get(cat_name, 0.0) + t.amount
            elif t.type == "INCOME":
                total_income += t.amount

        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Income", f"{total_income:,.2f} KZT")
        m2.metric("💸 Total Expense", f"{total_expense:,.2f} KZT")
        m3.metric("⚖️ Net Balance", f"{(total_income - total_expense):,.2f} KZT")

        st.divider()

        if expense_by_cat:
            st.subheader("🍩 Expense Structure")
            
            labels = list(expense_by_cat.keys())
            values = list(expense_by_cat.values())
            legend_labels = [f"{name}: {amt:,.2f} KZT" for name, amt in expense_by_cat.items()]

            fig = go.Figure(data=[go.Pie(
                labels=legend_labels,
                values=values,
                hole=0.6,
                textinfo='percent',
                hovertemplate='<b>%{label}</b><br>Share: %{percent}<extra></extra>',
                marker=dict(line=dict(color='#1e1e1e', width=2))
            )])

            fig.update_layout(
                annotations=[dict(
                    text=f"<b>{total_expense:,.2f} KZT</b><br><span style='font-size:13px;color:gray;'>EXPENSES</span>",
                    x=0.5, y=0.5,
                    font_size=18,
                    showarrow=False
                )],
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                margin=dict(t=20, b=20, l=20, r=20),
                height=420
            )

            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📜 Transaction History")

        data = []
        for t in transactions:
            cat = service.cat_repo.get_by_id(t.category_id)
            data.append({
                "ID": t.id,
                "Date": t.date,
                "Type": t.type,
                "Amount": f"{t.amount:.2f} {t.currency}",
                "Category": cat.name if cat else "N/A",
                "Description": t.description
            })
        st.dataframe(data, use_container_width=True)

        st.divider()
        st.subheader("🗑️ Delete Transaction")
        
        trx_map = {
            f"ID #{t.id} | {t.date} | {t.type} {t.amount:.2f} {t.currency} | {t.description}": t.id 
            for t in transactions
        }
        
        selected_trx_str = st.selectbox("Select transaction to delete:", list(trx_map.keys()))
        if st.button("🗑️ Delete Transaction", type="primary"):
            trx_id_to_delete = trx_map[selected_trx_str]
            if service.delete_transaction(trx_id_to_delete):
                st.success(f"Transaction #{trx_id_to_delete} successfully deleted!")
                st.rerun()
            else:
                st.error("Failed to delete transaction.")
    else:
        st.info("No transactions found yet. Add your first transaction in '➕ Add Transaction'.")

# 2. ADD TRANSACTION
elif menu == "➕ Add Transaction":
    st.header("➕ New Transaction")
    categories = service.cat_repo.get_all()
    cat_dict = {f"{c.name} ({c.type})": c.id for c in categories}

    with st.form("add_trx_form"):
        selected_cat_str = st.selectbox("Category", list(cat_dict.keys()))
        amount = st.number_input("Amount (KZT)", min_value=0.01, step=100.0)
        trx_type = st.selectbox("Type", ["EXPENSE", "INCOME"])
        date = st.date_input("Date", datetime.date.today()).strftime("%Y-%m-%d")
        description = st.text_input("Description")

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            if not description.strip():
                st.error("Please enter a transaction description!")
            else:
                try:
                    cat_id = cat_dict[selected_cat_str]
                    service.add_transaction(current_user.id, cat_id, amount, trx_type, date, description, currency="KZT")
                    st.success("Transaction added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

# 3. CATEGORIES WITH DELETE OPTION
elif menu == "🏷️ Categories":
    st.header("🏷️ Categories")
    with st.form("add_cat_form"):
        cat_name = st.text_input("Category Name")
        cat_type = st.selectbox("Type", ["EXPENSE", "INCOME"])
        if st.form_submit_button("Add Category"):
            if not cat_name.strip():
                st.error("Please enter a category name!")
            else:
                try:
                    service.add_category(cat_name, cat_type)
                    st.success(f"Category '{cat_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    categories = service.cat_repo.get_all()
    st.table([{"ID": c.id, "Category Name": c.name, "Type": c.type} for c in categories])

    if categories:
        st.divider()
        st.subheader("🗑️ Delete Category")
        cat_map = {f"ID #{c.id} | {c.name} ({c.type})": c.id for c in categories}
        selected_cat_str = st.selectbox("Select category to delete:", list(cat_map.keys()))
        
        if st.button("🗑️ Delete Category", type="primary"):
            cat_id_to_delete = cat_map[selected_cat_str]
            try:
                if service.delete_category(cat_id_to_delete):
                    st.success("Category deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete category.")
            except Exception as e:
                st.error(f"Error: {e}")

# 4. BUDGETS
elif menu == "🎯 Budgets":
    st.header("🎯 Monthly Budget Management")
    st.caption("Exceeding a budget triggers a layered notification chain (Decorator Pattern).")

    categories = [c for c in service.cat_repo.get_all() if c.type == "EXPENSE"]
    cat_dict = {c.name: c.id for c in categories}

    if cat_dict:
        with st.form("budget_form"):
            selected_cat_name = st.selectbox("Expense Category", list(cat_dict.keys()))
            limit = st.number_input("Monthly Limit (KZT)", min_value=1.0, step=1000.0)
            month_year = st.text_input("Month (Format YYYY-MM)", datetime.date.today().strftime("%Y-%m"))

            if st.form_submit_button("Set Budget"):
                if not month_year.strip():
                    st.error("Please specify a month in YYYY-MM format!")
                else:
                    try:
                        cat_id = cat_dict[selected_cat_name]
                        service.set_budget(current_user.id, cat_id, limit, month_year, currency="KZT")
                        st.success("Budget set successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No expense categories available to set a budget.")

# 5. BANK IMPORT (ADAPTER PATTERN)
elif menu == "🔌 Bank Import (Adapter)":
    st.header("🔌 Bank API Integration (Adapter Pattern)")
    st.write("Account format: KZ (2 letters) + 2 check digits + 3 bank digits + 13 account digits (20 characters total).")

    account_no = st.text_input("Bank Account Number (KZT IBAN)", value="KZ127221234567890123")
    if st.button("Import Statement"):
        if not account_no.strip():
            st.error("Please enter a bank account number!")
        else:
            try:
                bank_service = ThirdPartyBankApiService()
                adapter = BankApiAdapter(bank_service, account_no)
                
                default_cat = service.cat_repo.get_by_name("Bank Import")
                if not default_cat:
                    default_cat = service.add_category("Bank Import", "EXPENSE")

                count = service.import_external_transactions(current_user.id, adapter, default_cat.id)
                st.success(f"Successfully imported {count} transactions from external bank API!")
                st.rerun()
            except Exception as e:
                st.error(f"Import Error: {e}")

# 6. REPORT EXPORT (STRATEGY PATTERN)
elif menu == "📤 Export Report (Strategy)":
    st.header("📤 Report Generation (Strategy Pattern)")
    
    fmt = st.radio("Select export format:", ["CSV", "JSON", "TXT"])
    filename = st.text_input("File name (without extension)", value="financial_report")

    if st.button("Generate Report"):
        if not filename.strip():
            st.error("Please specify a file name for the report!")
        else:
            if fmt == "CSV":
                strat = CsvExportStrategy()
            elif fmt == "JSON":
                strat = JsonExportStrategy()
            else:
                strat = TxtExportStrategy()

            try:
                res_path = service.export_report(current_user.id, strat, filename.strip())
                st.success(f"Report generated and saved to: **{res_path}**")
            except Exception as e:
                st.error(f"Export Error: {e}")
