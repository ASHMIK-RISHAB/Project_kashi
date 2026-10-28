USE project_kashi;

-- 1. List all customers
SELECT * FROM CUSTOMER ORDER BY CustomerID;

-- 2. Show accounts with branch names
SELECT a.AccountNumber, a.AccountType, a.Balance, a.Status, b.BranchName
FROM ACCOUNT a JOIN BRANCH b ON a.BranchID = b.BranchID;

-- 3. List customers and their account numbers
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName, a.AccountNumber
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID;

-- 4. Total balance held in each branch
SELECT b.BranchName, SUM(a.Balance) AS TotalDeposits
FROM BRANCH b JOIN ACCOUNT a ON a.BranchID = b.BranchID
GROUP BY b.BranchID, b.BranchName;

-- 5. Number of accounts per account type
SELECT AccountType, COUNT(*) AS AccountCount
FROM ACCOUNT GROUP BY AccountType;

-- 6. Transaction history for each account
SELECT a.AccountNumber, t.TransactionType, t.Amount, t.TransactionDate, t.TransactionStatus
FROM ACCOUNT a JOIN BANK_TRANSACTION t ON a.AccountID = t.AccountID
ORDER BY t.TransactionDate DESC;

-- 7. Customers with no account
SELECT c.CustomerID, c.FirstName, c.LastName
FROM CUSTOMER c LEFT JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
WHERE ah.AccountID IS NULL;

-- 8. Customers with loan applications and their status
SELECT CONCAT(c.FirstName,' ',c.LastName) AS CustomerName, l.LoanType, l.LoanAmount, l.LoanStatus
FROM CUSTOMER c JOIN LOAN l ON c.CustomerID = l.CustomerID;

-- 9. Total payments recorded for each loan
SELECT l.LoanID, l.LoanType, COALESCE(SUM(p.Amount),0) AS TotalPayments
FROM LOAN l LEFT JOIN LOAN_PAYMENT p ON l.LoanID = p.LoanID
GROUP BY l.LoanID, l.LoanType;

-- 10. Accounts with balance above the average account balance
SELECT AccountNumber, Balance
FROM ACCOUNT
WHERE Balance > (SELECT AVG(Balance) FROM ACCOUNT);

-- 11. Branches with more than one employee (HAVING)
SELECT b.BranchName, COUNT(e.EmployeeID) AS EmployeeCount
FROM BRANCH b JOIN EMPLOYEE e ON e.BranchID = b.BranchID
GROUP BY b.BranchID, b.BranchName
HAVING COUNT(e.EmployeeID) > 1;

-- 12. View: customer account summary
CREATE OR REPLACE VIEW vw_customer_account_summary AS
SELECT c.CustomerID, CONCAT(c.FirstName,' ',c.LastName) AS CustomerName,
       a.AccountNumber, a.AccountType, a.Balance, b.BranchName
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID=c.CustomerID
JOIN ACCOUNT a ON a.AccountID=ah.AccountID
JOIN BRANCH b ON b.BranchID=a.BranchID;

SELECT * FROM vw_customer_account_summary;

-- 13. Stored procedure: customer accounts
DELIMITER //
CREATE PROCEDURE sp_customer_accounts(IN p_customer_id INT)
BEGIN
  SELECT a.AccountID, a.AccountNumber, a.AccountType, a.Balance, a.Status
  FROM ACCOUNT a JOIN ACCOUNT_HOLDER ah ON ah.AccountID=a.AccountID
  WHERE ah.CustomerID=p_customer_id;
END //
DELIMITER ;

-- Run: CALL sp_customer_accounts(1);

-- 14. Stored function: calculate simple interest (demonstration)
DELIMITER //
CREATE FUNCTION fn_simple_interest(p_principal DECIMAL(14,2), p_rate DECIMAL(5,2), p_years DECIMAL(8,2))
RETURNS DECIMAL(14,2)
DETERMINISTIC
RETURN (p_principal * p_rate * p_years / 100) //
DELIMITER ;

-- Run: SELECT fn_simple_interest(50000, 8.5, 2);

-- 15. Trigger: reject invalid negative balances (additional DB-level safeguard)
DELIMITER //
CREATE TRIGGER trg_account_nonnegative_balance
BEFORE UPDATE ON ACCOUNT
FOR EACH ROW
BEGIN
  IF NEW.Balance < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account balance cannot be negative';
  END IF;
END //
DELIMITER ;
