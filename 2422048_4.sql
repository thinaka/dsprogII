SELECT SUM(price * quantity) 
AS total_sales
FROM orders
INNER JOIN products AS pro
ON orders.product_id = pro.product_id
INNER JOIN customers AS cus
ON orders.customer_id = cus.customer_id
WHERE order_date
BETWEEN '2024-01-01 00:00:00'
AND '2024-03-30 23:59:59'
AND gender = 'Female'
AND age >= 20;