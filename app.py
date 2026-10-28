import os
from decimal import Decimal, InvalidOperation
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-for-local-college-project")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "project_kashi"),
        autocommit=False
    )

def db_error_message(exc):
    return f"Database error: {exc}. Check MySQL is running and database.sql has been imported."

@app.route("/")
def index():
    stats = {"customers": 0, "accounts": 0, "transactions": 0, "loans": 0}
    try:
        conn = get_db()
        cur = conn.cursor()
        for key, table in [("customers","CUSTOMER"),("accounts","ACCOUNT"),("transactions","BANK_TRANSACTION"),("loans","LOAN")]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            stats[key] = cur.fetchone()[0]
        cur.close()
        conn.close()
    except Error as e:
        flash(db_error_message(e), "error")
    return render_template("index.html", stats=stats)

@app.route("/customers")
def customers():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM CUSTOMER ORDER BY CustomerID DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("customers.html", customers=rows)

@app.route("/customers/new", methods=["GET", "POST"])
def new_customer():
    if request.method == "POST":
        data = (
            request.form.get("first_name","").strip(),
            request.form.get("last_name","").strip(),
            request.form.get("dob") or None,
            request.form.get("gender") or None,
            request.form.get("mobile","").strip(),
            request.form.get("email","").strip() or None,
            request.form.get("address","").strip() or None,
            request.form.get("city","").strip() or None,
        )
        if not data[0] or not data[1] or not data[4]:
            flash("First name, last name and mobile are required.", "error")
            return render_template("customer_form.html")
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""INSERT INTO CUSTOMER
                (FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (*data, date.today()))
            conn.commit()
            flash(f"Customer registered. Customer ID: {cur.lastrowid}", "success")
            return redirect(url_for("customers"))
        except Error as e:
            conn.rollback(); flash(db_error_message(e), "error")
        finally:
            cur.close(); conn.close()
    return render_template("customer_form.html")

@app.route("/accounts")
def accounts():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT a.*, b.BranchName,
        GROUP_CONCAT(CONCAT(c.FirstName,' ',c.LastName) SEPARATOR ', ') AS Holders
        FROM ACCOUNT a JOIN BRANCH b ON a.BranchID=b.BranchID
        LEFT JOIN ACCOUNT_HOLDER ah ON a.AccountID=ah.AccountID
        LEFT JOIN CUSTOMER c ON c.CustomerID=ah.CustomerID
        GROUP BY a.AccountID ORDER BY a.AccountID DESC""")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("accounts.html", accounts=rows)

@app.route("/accounts/new", methods=["GET","POST"])
def new_account():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT CustomerID, FirstName, LastName FROM CUSTOMER ORDER BY FirstName")
    customers = cur.fetchall()
    cur.execute("SELECT BranchID, BranchName FROM BRANCH ORDER BY BranchName")
    branches = cur.fetchall()
    cur.close(); conn.close()
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        branch_id = request.form.get("branch_id")
        account_type = request.form.get("account_type")
        try:
            opening = Decimal(request.form.get("opening_balance","0"))
            if opening < 0: raise InvalidOperation
        except (InvalidOperation, ValueError):
            flash("Opening balance must be zero or greater.", "error")
            return render_template("account_form.html", customers=customers, branches=branches)
        conn = get_db(); cur = conn.cursor()
        try:
            conn.start_transaction()
            cur.execute("""INSERT INTO ACCOUNT (AccountNumber, AccountType, OpeningDate, Balance, Status, BranchID)
                           VALUES (CONCAT('KSH', LPAD(UUID_SHORT() MOD 100000000, 8, '0')), %s, %s, %s, 'Active', %s)""",
                        (account_type, date.today(), opening, branch_id))
            account_id = cur.lastrowid
            cur.execute("INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderSince, HolderType) VALUES (%s,%s,%s,'Primary')",
                        (customer_id, account_id, date.today()))
            if opening > 0:
                cur.execute("""INSERT INTO BANK_TRANSACTION
                    (AccountID, TransactionType, Amount, TransactionDate, Description, ReferenceNumber, TransactionStatus)
                    VALUES (%s,'DEPOSIT',%s,NOW(),'Opening deposit',CONCAT('OPEN-',%s),'SUCCESS')""",
                    (account_id, opening, account_id))
            conn.commit()
            flash(f"Account created successfully. Account ID: {account_id}", "success")
            return redirect(url_for("accounts"))
        except Error as e:
            conn.rollback(); flash(db_error_message(e), "error")
        finally:
            cur.close(); conn.close()
    return render_template("account_form.html", customers=customers, branches=branches)

@app.route("/transactions", methods=["GET","POST"])
def transactions():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT AccountID, AccountNumber, Balance FROM ACCOUNT WHERE Status='Active' ORDER BY AccountID")
    accounts = cur.fetchall()
    if request.method == "POST":
        kind = request.form.get("kind")
        try:
            amount = Decimal(request.form.get("amount","0"))
            if amount <= 0: raise InvalidOperation
        except (InvalidOperation, ValueError):
            flash("Enter a valid amount greater than zero.", "error")
            cur.close(); conn.close()
            return redirect(url_for("transactions"))
        source_id = request.form.get("account_id")
        dest_id = request.form.get("destination_id")
        description = request.form.get("description","").strip() or kind.title()
        try:
            conn.rollback()
            conn.start_transaction()
            cur.execute("SELECT AccountID, Balance FROM ACCOUNT WHERE AccountID=%s AND Status='Active' FOR UPDATE", (source_id,))
            source = cur.fetchone()
            if not source:
                raise ValueError("Source account not found or inactive.")
            if kind in ("WITHDRAWAL","TRANSFER") and Decimal(str(source["Balance"])) < amount:
                raise ValueError("Insufficient balance.")
            if kind == "DEPOSIT":
                cur.execute("UPDATE ACCOUNT SET Balance=Balance+%s WHERE AccountID=%s", (amount, source_id))
                cur.execute("""INSERT INTO BANK_TRANSACTION (AccountID,TransactionType,Amount,TransactionDate,Description,ReferenceNumber,TransactionStatus)
                               VALUES (%s,'DEPOSIT',%s,NOW(),%s,UUID(),'SUCCESS')""", (source_id, amount, description))
            elif kind == "WITHDRAWAL":
                cur.execute("UPDATE ACCOUNT SET Balance=Balance-%s WHERE AccountID=%s", (amount, source_id))
                cur.execute("""INSERT INTO BANK_TRANSACTION (AccountID,TransactionType,Amount,TransactionDate,Description,ReferenceNumber,TransactionStatus)
                               VALUES (%s,'WITHDRAWAL',%s,NOW(),%s,UUID(),'SUCCESS')""", (source_id, amount, description))
            elif kind == "TRANSFER":
                if str(source_id) == str(dest_id): raise ValueError("Choose a different destination account.")
                cur.execute("SELECT AccountID FROM ACCOUNT WHERE AccountID=%s AND Status='Active' FOR UPDATE", (dest_id,))
                if not cur.fetchone(): raise ValueError("Destination account not found or inactive.")
                cur.execute("UPDATE ACCOUNT SET Balance=Balance-%s WHERE AccountID=%s", (amount, source_id))
                cur.execute("UPDATE ACCOUNT SET Balance=Balance+%s WHERE AccountID=%s", (amount, dest_id))
                ref = "TRF-" + str(source_id) + "-" + str(dest_id) + "-" + str(date.today())
                cur.execute("""INSERT INTO BANK_TRANSACTION (AccountID,TransactionType,Amount,TransactionDate,Description,ReferenceNumber,TransactionStatus)
                               VALUES (%s,'TRANSFER_OUT',%s,NOW(),%s,%s,'SUCCESS')""", (source_id, amount, description, ref))
                cur.execute("""INSERT INTO BANK_TRANSACTION (AccountID,TransactionType,Amount,TransactionDate,Description,ReferenceNumber,TransactionStatus)
                               VALUES (%s,'TRANSFER_IN',%s,NOW(),%s,%s,'SUCCESS')""", (dest_id, amount, description, ref))
            else:
                raise ValueError("Invalid transaction type.")
            conn.commit()
            flash("Transaction completed successfully.", "success")
        except ValueError as e:
            conn.rollback(); flash(str(e), "error")
        except Error as e:
            conn.rollback(); flash(db_error_message(e), "error")
        finally:
            cur.close(); conn.close()
        return redirect(url_for("transactions"))
    cur.execute("""SELECT t.*, a.AccountNumber FROM BANK_TRANSACTION t
                   JOIN ACCOUNT a ON a.AccountID=t.AccountID ORDER BY t.TransactionID DESC LIMIT 100""")
    history = cur.fetchall()
    cur.close(); conn.close()
    return render_template("transactions.html", accounts=accounts, history=history)

@app.route("/loans", methods=["GET","POST"])
def loans():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("loan_amount","0"))
            rate = Decimal(request.form.get("interest_rate","0"))
            tenure = int(request.form.get("tenure","0"))
            if amount <= 0 or rate < 0 or tenure <= 0: raise ValueError
            cur.execute("""INSERT INTO LOAN (CustomerID,BranchID,LoanType,LoanAmount,InterestRate,StartDate,TenureMonths,LoanStatus)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,'Pending')""",
                        (request.form.get("customer_id"),request.form.get("branch_id"),request.form.get("loan_type"),amount,rate,date.today(),tenure))
            conn.commit(); flash("Loan application recorded with Pending status.", "success")
        except (ValueError, InvalidOperation):
            conn.rollback(); flash("Enter valid loan amount, interest rate and tenure.", "error")
        except Error as e:
            conn.rollback(); flash(db_error_message(e), "error")
        finally:
            cur.close(); conn.close()
        return redirect(url_for("loans"))
    cur.execute("SELECT CustomerID, FirstName, LastName FROM CUSTOMER ORDER BY FirstName")
    customers = cur.fetchall()
    cur.execute("SELECT BranchID, BranchName FROM BRANCH ORDER BY BranchName")
    branches = cur.fetchall()
    cur.execute("""SELECT l.*, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName, b.BranchName
                   FROM LOAN l JOIN CUSTOMER c ON c.CustomerID=l.CustomerID
                   JOIN BRANCH b ON b.BranchID=l.BranchID ORDER BY l.LoanID DESC""")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("loans.html", customers=customers, branches=branches, loans=rows)

@app.route("/loan-payments", methods=["GET","POST"])
def loan_payments():
    conn = get_db(); cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount","0"))
            if amount <= 0: raise ValueError
            cur.execute("SELECT LoanID FROM LOAN WHERE LoanID=%s", (request.form.get("loan_id"),))
            if not cur.fetchone(): raise ValueError
            cur.execute("""INSERT INTO LOAN_PAYMENT (LoanID,PaymentDate,Amount,PaymentMode,ReferenceNumber)
                           VALUES (%s,%s,%s,%s,UUID())""",
                        (request.form.get("loan_id"),date.today(),amount,request.form.get("payment_mode")))
            conn.commit(); flash("Loan payment recorded.", "success")
        except (ValueError, InvalidOperation):
            conn.rollback(); flash("Check the loan ID and payment amount.", "error")
        except Error as e:
            conn.rollback(); flash(db_error_message(e), "error")
        finally:
            cur.close(); conn.close()
        return redirect(url_for("loan_payments"))
    cur.execute("SELECT LoanID, LoanType, LoanAmount, LoanStatus FROM LOAN ORDER BY LoanID DESC")
    loans = cur.fetchall()
    cur.execute("""SELECT p.*, l.LoanType FROM LOAN_PAYMENT p JOIN LOAN l ON l.LoanID=p.LoanID
                   ORDER BY p.PaymentID DESC""")
    payments = cur.fetchall()
    cur.close(); conn.close()
    return render_template("loan_payments.html", loans=loans, payments=payments)

if __name__ == "__main__":
    app.run(debug=True)
