CREATE DATABASE IF NOT EXISTS Sales_Management_System;
USE Sales_Management_System;

DROP TABLE IF EXISTS payment_splits;
DROP TABLE IF EXISTS customer_sales;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS branches;
-- ─────────────────────────────────────────────
-- TABLES

CREATE TABLE branches (
    branch_id         INT          NOT NULL PRIMARY KEY,
    branch_name       VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

CREATE TABLE customer_sales (
    sale_id         INT            NOT NULL AUTO_INCREMENT PRIMARY KEY,  -- auto inc generted value for this column 
    branch_id       INT            NOT NULL,
    sale_date       DATE           NOT NULL,
    customer_name   VARCHAR(100)   NOT NULL,
    mobile_number   VARCHAR(15)    UNIQUE,
    product_name    VARCHAR(50),
    gross_sales     DECIMAL(12,2)  NOT NULL,
    received_amount DECIMAL(12,2)  DEFAULT 0,
    pending_amount  DECIMAL(12,2)  GENERATED ALWAYS AS (gross_sales - received_amount) STORED, -- col is gen'd nd value stored in STORED
    status          ENUM('Open','Closed')   DEFAULT 'Open',
    CONSTRAINT FK_customer_sales_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE users (
    user_id       INT          NOT NULL PRIMARY KEY,
    username      VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email         VARCHAR(255) UNIQUE,
    branch_id     INT,
    role          ENUM ('Super Admin', 'Admin'),
    CONSTRAINT FK_users_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE payment_splits (
    payment_id     INT            NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    sale_id        INT            NOT NULL,
    payment_date   DATE           NOT NULL,
    amount_paid    DECIMAL(12,2)  NOT NULL,
    payment_method VARCHAR(50),
    CONSTRAINT FK_payment_sales
        FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
);

-- SAMPLE DATA
INSERT INTO branches (branch_id, branch_name, branch_admin_name) VALUES
(1,    'Chennai',       'Arun Kumar'),
(2,    'Bangalore',     'Rahul Sharma'),
(3,    'Hyderabad',     'Kiran Reddy'),
(1000, 'All locations', 'Prasad Ram');

SELECT * FROM branches;

INSERT INTO users (user_id, username, password_hash, email, branch_id, role) VALUES
(1, 'superadmin',      'admin123', 'superadmin@gmail.com', 1000, 'Super Admin'),
(2, 'chennaiadmin',    'admin123', 'chennai@gmail.com',    1,    'Admin'),
(3, 'bangaloreadmin',  'admin123', 'bangalore@gmail.com',  2,    'Admin'),
(4, 'hyderabadadmin',  'admin123', 'hyderbad@gmail.com',   3,    'Admin');


INSERT INTO customer_sales
    (branch_id, sale_date, customer_name, mobile_number, product_name, gross_sales)
VALUES
(1, '2026-05-01', 'Ravi',    '9876543210', 'DS',  50000),
(2, '2026-05-02', 'Priya',   '9876543211', 'DA',  65000),
(1, '2026-05-03', 'Karthik', '9876543212', 'FSD', 70000);

INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method) VALUES
(1, '2026-05-04', 20000, 'UPI'),
(1, '2026-05-05', 30000, 'Card'),
(2, '2026-05-06', 40000, 'Cash');

-- TRIGGER

DROP TRIGGER IF EXISTS trg_update_received_amount;  -- cancels if there is another trigger stored
-- Delimiter passes code as a single block (runs in one piece)
DELIMITER $$

CREATE TRIGGER trg_update_received_after_payment
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    -- Declare variable to avoid reading payment_splits inside SET clause
    DECLARE v_total_paid DECIMAL(12,2);

    -- Step 1: Calculate total received into a variable
    SELECT COALESCE(SUM(amount_paid), 0)
    INTO v_total_paid
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;

    -- Step 2: update status
    UPDATE customer_sales
    SET
        received_amount = v_total_paid,
        status = CASE
                     WHEN (gross_sales - v_total_paid) <= 0 THEN 'Closed'
                     ELSE 'Open'
                 END
    WHERE sale_id = NEW.sale_id;

END$$

DELIMITER ;

-- TEST TRIGGER

INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
VALUES (2, '2026-06-04', 10000, 'UPI');
-- VIEW ALL TABLES
SELECT * FROM branches;
SELECT * FROM customer_sales;
SELECT * FROM users;
SELECT * FROM payment_splits;

-- KPI query calcs

SELECT
    SUM(gross_sales)     AS total_sales,
    SUM(received_amount) AS total_received,
    SUM(pending_amount)  AS total_pending
FROM customer_sales;