-- SQLite Database Schema for Personal Finance System (KZT)

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    role TEXT DEFAULT 'USER'
);

-- 2. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('INCOME', 'EXPENSE'))
);

-- 3. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    type TEXT NOT NULL CHECK(type IN ('INCOME', 'EXPENSE')),
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    currency TEXT DEFAULT 'KZT',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- 4. Budgets Table
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    monthly_limit REAL NOT NULL CHECK(monthly_limit > 0),
    month_year TEXT NOT NULL, -- Format: YYYY-MM
    currency TEXT DEFAULT 'KZT',
    UNIQUE(user_id, category_id, month_year),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- Initial Seed Data
INSERT OR IGNORE INTO users (id, username, email, role)
VALUES (1, 'default_user', 'user@example.com', 'USER');

INSERT OR IGNORE INTO categories (name, type) VALUES
('Salary', 'INCOME'),
('Groceries', 'EXPENSE'),
('Bank Import', 'EXPENSE');