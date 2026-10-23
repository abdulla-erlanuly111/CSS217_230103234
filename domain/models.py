from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    role: str = "USER"

@dataclass
class Category:
    id: Optional[int]
    name: str
    type: str  # "INCOME" или "EXPENSE"

@dataclass
class Transaction:
    id: Optional[int]
    user_id: int
    category_id: int
    amount: float
    type: str  # "INCOME" или "EXPENSE"
    date: str  # "YYYY-MM-DD"
    description: str
    currency: str = "KZT"

@dataclass
class Budget:
    id: Optional[int]
    user_id: int
    category_id: int
    monthly_limit: float
    month_year: str  # "YYYY-MM"
    currency: str = "KZT"
