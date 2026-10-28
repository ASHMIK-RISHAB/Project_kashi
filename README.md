# Project KASHI — Banking Management System

A college DBMS demonstration project using raw HTML/CSS, Python Flask and MySQL. It is a local educational simulation, **not a real banking system**.

## Features
- Customer registration stored in MySQL
- Account creation linked to a customer and branch
- Deposits, withdrawals and account-to-account transfers
- Transaction history
- Loan application and loan-payment recording
- Eight relational tables, primary/foreign keys, constraints, indexes and SQL business queries

## Requirements
- Python 3.10+
- MySQL Server 8.0+
- MySQL Workbench (recommended)
- Web browser

## Setup on Windows
1. Install and start MySQL Server.
2. Open MySQL Workbench, connect to your local server, open `database.sql`, and execute the whole script.
3. Extract this project folder.
4. Open Command Prompt in the project folder and run:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Set your MySQL password for this terminal session (replace the example):
   ```bat
   set DB_PASSWORD=your_mysql_password
   ```
   If your MySQL root user has no password, you can leave DB_PASSWORD unset.
6. Run:
   ```bat
   py app.py
   ```
7. Open `http://127.0.0.1:5000`.

## First demo
- Demo customer ID is 1 and demo account ID is 1 (if the SQL script was run on an empty database).
- Register another customer.
- Open an account for that customer.
- Make a deposit, then a withdrawal.
- Transfer money to another active account.
- Verify the balance and transaction history.

## Important
- Never use real customer data or real banking credentials.
- This demo is not production-grade: it has no authentication/authorization, CSRF protection, audit-grade ledger, or deployment hardening.
- Use only on localhost for the classroom demonstration.
