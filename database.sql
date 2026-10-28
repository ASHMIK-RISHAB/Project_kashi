CREATE DATABASE IF NOT EXISTS project_kashi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE project_kashi;

CREATE TABLE IF NOT EXISTS CUSTOMER (
  CustomerID INT AUTO_INCREMENT PRIMARY KEY,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  DateOfBirth DATE NULL,
  Gender ENUM('Male','Female','Other') NULL,
  Mobile VARCHAR(15) NOT NULL,
  Email VARCHAR(120) UNIQUE NULL,
  Address VARCHAR(255) NULL,
  City VARCHAR(80) NULL,
  RegistrationDate DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE IF NOT EXISTS BRANCH (
  BranchID INT AUTO_INCREMENT PRIMARY KEY,
  BranchName VARCHAR(100) NOT NULL,
  IFSCCode VARCHAR(11) NOT NULL UNIQUE,
  Address VARCHAR(255) NOT NULL,
  City VARCHAR(80) NOT NULL,
  State VARCHAR(80) NOT NULL,
  ContactNumber VARCHAR(15) NOT NULL
);

CREATE TABLE IF NOT EXISTS EMPLOYEE (
  EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
  EmployeeName VARCHAR(100) NOT NULL,
  Mobile VARCHAR(15) NOT NULL,
  Email VARCHAR(120) UNIQUE,
  Designation VARCHAR(60) NOT NULL,
  Salary DECIMAL(12,2) NOT NULL CHECK (Salary >= 0),
  JoiningDate DATE NOT NULL,
  BranchID INT NOT NULL,
  CONSTRAINT fk_employee_branch FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
);

CREATE TABLE IF NOT EXISTS ACCOUNT (
  AccountID INT AUTO_INCREMENT PRIMARY KEY,
  AccountNumber VARCHAR(20) NOT NULL UNIQUE,
  AccountType ENUM('Saving','Current','Salary') NOT NULL,
  OpeningDate DATE NOT NULL,
  Balance DECIMAL(14,2) NOT NULL DEFAULT 0 CHECK (Balance >= 0),
  Status ENUM('Active','Inactive','Close') NOT NULL DEFAULT 'Active',
  BranchID INT NOT NULL,
  CONSTRAINT fk_account_branch FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
);

CREATE TABLE IF NOT EXISTS ACCOUNT_HOLDER (
  CustomerID INT NOT NULL,
  AccountID INT NOT NULL,
  HolderSince DATE NOT NULL,
  HolderType ENUM('Primary','Joint') NOT NULL DEFAULT 'Primary',
  PRIMARY KEY (CustomerID, AccountID),
  CONSTRAINT fk_holder_customer FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID),
  CONSTRAINT fk_holder_account FOREIGN KEY (AccountID) REFERENCES ACCOUNT(AccountID)
);

CREATE TABLE IF NOT EXISTS BANK_TRANSACTION (
  TransactionID BIGINT AUTO_INCREMENT PRIMARY KEY,
  AccountID INT NOT NULL,
  TransactionType ENUM('DEPOSIT','WITHDRAWAL','TRANSFER_IN','TRANSFER_OUT') NOT NULL,
  Amount DECIMAL(14,2) NOT NULL CHECK (Amount > 0),
  TransactionDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Description VARCHAR(255),
  ReferenceNumber VARCHAR(80) NOT NULL,
  TransactionStatus ENUM('SUCCESS','FAILED','PENDING') NOT NULL DEFAULT 'SUCCESS',
  CONSTRAINT fk_transaction_account FOREIGN KEY (AccountID) REFERENCES ACCOUNT(AccountID),
  INDEX idx_transaction_account_date (AccountID, TransactionDate)
);

CREATE TABLE IF NOT EXISTS LOAN (
  LoanID INT AUTO_INCREMENT PRIMARY KEY,
  CustomerID INT NOT NULL,
  BranchID INT NOT NULL,
  LoanType ENUM('Home Loan','Education Loan','Personal Loan','Vehicle Loan') NOT NULL,
  LoanAmount DECIMAL(14,2) NOT NULL CHECK (LoanAmount > 0),
  InterestRate DECIMAL(5,2) NOT NULL CHECK (InterestRate >= 0),
  StartDate DATE NOT NULL,
  TenureMonths INT NOT NULL CHECK (TenureMonths > 0),
  LoanStatus ENUM('Pending','Approved','Rejected','Closed') NOT NULL DEFAULT 'Pending',
  CONSTRAINT fk_loan_customer FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID),
  CONSTRAINT fk_loan_branch FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID)
);

CREATE TABLE IF NOT EXISTS LOAN_PAYMENT (
  PaymentID INT AUTO_INCREMENT PRIMARY KEY,
  LoanID INT NOT NULL,
  PaymentDate DATE NOT NULL,
  Amount DECIMAL(14,2) NOT NULL CHECK (Amount > 0),
  PaymentMode ENUM('Cash','UPI','Card','Bank Transfer') NOT NULL,
  ReferenceNumber VARCHAR(80) NOT NULL UNIQUE,
  CONSTRAINT fk_payment_loan FOREIGN KEY (LoanID) REFERENCES LOAN(LoanID)
);

INSERT IGNORE INTO BRANCH (BranchID, BranchName, IFSCCode, Address, City, State, ContactNumber) VALUES
(1,'Kashi Main Branch','KASH0000001','College Road','Mangalore','Karnataka','9000000001'),
(2,'Kashi City Branch','KASH0000002','Market Road','Mangalore','Karnataka','9000000002');

INSERT IGNORE INTO EMPLOYEE (EmployeeID,EmployeeName,Mobile,Email,Designation,Salary,JoiningDate,BranchID) VALUES
(1,'Ayaan Rahman','9000000011','ayaan@example.com','Branch Manager',65000,'2024-06-01',1),
(2,'Sara Khan','9000000012','sara@example.com','Bank Officer',42000,'2025-01-15',2);

-- Optional demo data; these rows are inserted only once by their primary keys.
INSERT IGNORE INTO CUSTOMER (CustomerID,FirstName,LastName,DateOfBirth,Gender,Mobile,Email,Address,City,RegistrationDate) VALUES
(1,'Demo','Customer','2005-01-10','Other','9000000101','demo.customer@example.com','Sample Address','Mangalore',CURRENT_DATE);

INSERT IGNORE INTO ACCOUNT (AccountID,AccountNumber,AccountType,OpeningDate,Balance,Status,BranchID) VALUES
(1,'KSH00000001','Saving',CURRENT_DATE,5000.00,'Active',1);
INSERT IGNORE INTO ACCOUNT_HOLDER (CustomerID,AccountID,HolderSince,HolderType) VALUES (1,1,CURRENT_DATE,'Primary');
INSERT IGNORE INTO BANK_TRANSACTION (TransactionID,AccountID,TransactionType,Amount,Description,ReferenceNumber,TransactionStatus)
VALUES (1,1,'DEPOSIT',5000.00,'Demo opening balance','DEMO-OPEN-1','SUCCESS');
INSERT IGNORE INTO LOAN (LoanID,CustomerID,BranchID,LoanType,LoanAmount,InterestRate,StartDate,TenureMonths,LoanStatus)
VALUES (1,1,1,'Education Loan',50000.00,8.5,CURRENT_DATE,24,'Pending');
