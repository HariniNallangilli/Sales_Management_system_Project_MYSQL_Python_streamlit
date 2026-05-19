CREATE DATABASE IF NOT EXISTS Sales_Management_System_Queries_Responses;
use Sales_Management_System_Queries_Responses;

-- Basic Queries
-- Q1: Retrieve all records from customer_sales
SELECT * FROM customer_sales;
-- Q2: Retrieve all records from branches
SELECT * FROM branches;
-- Q3: Retrieve all records from payment_splits
SELECT * FROM payment_splits;
-- Q4: Display all sales with status = 'Open'
SELECT * FROM customer_sales
WHERE status = 'Open';

-- Aggregation Queries
-- Q6: Total gross sales across all branches
SELECT ROUND(SUM(gross_sales), 2) AS Total_Gross_Sales
FROM customer_sales;
-- Q7: Total received amount across all sales
SELECT ROUND(SUM(received_amount), 2) AS Total_Received_Amount
FROM customer_sales;
-- Q8: Total pending amount across all sales
SELECT ROUND(SUM(pending_amount), 2) AS Total_Pending_Amount
FROM customer_sales;
-- Q9: Count of sales per branch
SELECT b.branch_name,
       COUNT(cs.sale_id) AS Total_Sales
FROM customer_sales cs
LEFT JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY Total_Sales ASC;

-- Q10: Find the average gross sales amount.
SELECT cs.branch_id,b.branch_name,AVG(cs.gross_sales) as Avg_sales
FROM customer_sales cs
LEFT JOIN branches b 
ON b.branch_id=cs.branch_id
GROUP BY cs.branch_id;

-- Join-Based Queries
-- Q11: Sales details with branch name
SELECT cs.sale_id, b.branch_name,b.branch_id, cs.sale_date, cs.customer_name,
       cs.product_name, cs.gross_sales, cs.received_amount,
       cs.pending_amount, cs.status
FROM customer_sales cs
LEFT JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_date;

-- Q12: Sales details with total payment received (via payment_splits)
SELECT cs.sale_id, cs.customer_name, cs.gross_sales,
       ROUND(COALESCE(SUM(ps.amount_paid), 0), 2) AS Total_payment_received_Via_Splits,
       cs.pending_amount
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.customer_name, cs.gross_sales, cs.pending_amount
ORDER BY cs.sale_id;

-- Q13: Branch-wise total gross sales
SELECT b.branch_name,
       ROUND(SUM(cs.gross_sales), 2)      AS Total_Gross_Sales,
       ROUND(SUM(cs.received_amount), 2)  AS Total_Received,
       ROUND(SUM(cs.pending_amount), 2)   AS Total_Pending
FROM customer_sales cs
LEFT JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY Total_Gross_Sales DESC;

-- Q14: Sales along with payment method used
SELECT cs.sale_id, cs.customer_name, cs.gross_sales,
       ps.payment_date, ps.amount_paid, ps.payment_method
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_date;

-- Financial Tracking Queries
-- Q16: Sales where pending amount is greater than 5000
SELECT cs.sale_id, b.branch_name, cs.customer_name,
       cs.gross_sales, cs.received_amount, cs.pending_amount
FROM customer_sales cs
LEFT JOIN branches b ON cs.branch_id = b.branch_id
WHERE cs.pending_amount > 5000;

Q17: Top 3 highest gross sales
SELECT cs.sale_id, b.branch_name, cs.customer_name,
       cs.product_name, cs.gross_sales
FROM customer_sales cs
LEFT JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.gross_sales DESC
LIMIT 3;

Q18: Payment method-wise total collection
SELECT payment_method,
count(payment_method) ,
sum(amount_paid)
       
FROM payment_splits
GROUP BY payment_method;

