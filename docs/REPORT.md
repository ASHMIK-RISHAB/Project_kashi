# PROJECT KASHI
## Banking Management System — DBMS Project Report

**Technology:** HTML, CSS, Python Flask, MySQL  
**Purpose:** Academic demonstration of relational database design and a three-layer web application. This is not a real banking product.

## 1. Problem statement
Manual or disconnected records make it difficult to manage customers, accounts, branches, employees, financial transactions and loan records consistently. Project KASHI models these records in a relational database and provides a web interface to demonstrate core operations.

## 2. Objectives
1. Design a relational database for a banking scenario.
2. Use primary keys and foreign keys to preserve referential integrity.
3. Insert customer and account data through HTML forms and Flask routes.
4. Demonstrate deposits, withdrawals and transfers with database transactions.
5. Query related records using joins and aggregate functions.
6. Document entities, relationships, cardinalities and business SQL queries.

## 3. System architecture
**Presentation layer:** HTML forms and CSS templates render pages and collect user input.  
**Application layer:** Flask receives requests, validates values, runs parameterized SQL and commits or rolls back transactions.  
**Database layer:** MySQL stores the records and enforces keys and constraints.

Flow: Browser → Flask route → MySQL query/transaction → Flask response → Browser.

## 4. Entities and attributes
- **CUSTOMER:** CustomerID (PK), FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate.
- **BRANCH:** BranchID (PK), BranchName, IFSCCode (unique), Address, City, State, ContactNumber.
- **EMPLOYEE:** EmployeeID (PK), EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID (FK).
- **ACCOUNT:** AccountID (PK), AccountNumber (unique), AccountType, OpeningDate, Balance, Status, BranchID (FK).
- **ACCOUNT_HOLDER:** CustomerID (PK/FK), AccountID (PK/FK), HolderSince, HolderType. Composite primary key permits a customer-account pair only once.
- **BANK_TRANSACTION:** TransactionID (PK), AccountID (FK), TransactionType, Amount, TransactionDate, Description, ReferenceNumber, TransactionStatus.
- **LOAN:** LoanID (PK), CustomerID (FK), BranchID (FK), LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus.
- **LOAN_PAYMENT:** PaymentID (PK), LoanID (FK), PaymentDate, Amount, PaymentMode, ReferenceNumber (unique).

`BANK_TRANSACTION` is used instead of the SQL keyword `TRANSACTION` as a table name, avoiding keyword conflicts.

## 5. Relationships and cardinality
1. BRANCH 1 : N EMPLOYEE — each employee belongs to one branch; a branch may have many employees.
2. BRANCH 1 : N ACCOUNT — each account belongs to one branch; a branch may maintain many accounts.
3. CUSTOMER M : N ACCOUNT through ACCOUNT_HOLDER — a customer may hold multiple accounts and an account may have joint holders.
4. ACCOUNT 1 : N BANK_TRANSACTION — an account can have many transaction records; each record belongs to one account.
5. CUSTOMER 1 : N LOAN — a customer may apply for many loans; each loan belongs to one customer.
6. BRANCH 1 : N LOAN — a branch may handle many loans; each loan is associated with one branch.
7. LOAN 1 : N LOAN_PAYMENT — a loan can have many payments; each payment belongs to one loan.

## 6. Normalization
- **1NF:** Each field stores a single value; repeating groups are not stored in one column.
- **2NF:** ACCOUNT_HOLDER has a composite key (CustomerID, AccountID); HolderSince and HolderType describe that complete association.
- **3NF:** Customer, branch, employee, account, transaction and loan facts are separated into entities so non-key attributes do not depend on unrelated entities. Branch details are not repeated in each account; customer details are not repeated in transaction rows.

## 7. Constraints and integrity
- Primary keys uniquely identify rows.
- Foreign keys prevent references to missing customers, branches, accounts or loans.
- NOT NULL enforces required fields.
- UNIQUE prevents duplicate IFSC codes, account numbers, emails where supplied, and loan-payment references.
- CHECK constraints enforce nonnegative balances/salaries and positive transaction/loan/payment amounts.
- ENUM columns restrict status and transaction-type values.
- Parameterized SQL is used for form input.
- Deposits, withdrawals and transfers use commit/rollback; account rows are locked during transaction processing.

## 8. Core workflows
### Customer registration
User submits a form → Flask checks required fields → parameterized INSERT → MySQL saves customer → success message and customer list.

### Account creation
User selects customer and branch → Flask inserts account → inserts ACCOUNT_HOLDER link → optionally records opening deposit → commits all changes together.

### Deposit/withdrawal
Flask validates a positive amount → locks account row → updates balance and inserts transaction history → commits both changes together. Withdrawal is rejected when balance is insufficient.

### Transfer
Flask locks and validates source/destination accounts → checks sufficient funds → debits source and credits destination → inserts TRANSFER_OUT and TRANSFER_IN records → commits all operations together. On error, changes are rolled back.

## 9. Limitations
This is a classroom prototype. It has no user login, role-based authorization, CSRF protection, production-grade ledger reconciliation, regulatory controls or deployment hardening. Do not expose it to the public internet or use real personal/financial data.

## 10. Conclusion
Project KASHI demonstrates how a relational database and a Flask application can model connected banking entities, preserve referential integrity, and process basic financial operations consistently. The design highlights keys, constraints, joins, normalization and transactions.

## 11. Screenshots to add before submission
Capture screenshots of:
1. Dashboard
2. Customer list and successful customer registration
3. Account list and account creation
4. Deposit and withdrawal results
5. Transfer history showing TRANSFER_OUT and TRANSFER_IN
6. MySQL Workbench table list and sample query output
7. ER diagram
