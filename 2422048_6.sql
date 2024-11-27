SELECT customer_name, price * quantity
AS total_purchase
FROM orders
INNER JOIN products AS pro
ON orders.product_id = pro.product_id
INNER JOIN customers AS cus
ON orders.customer_id = cus.customer_id
WHERE order_date
BETWEEN '2025-01-01 00:00:00'
AND '2025-06-30 23:59:59'
ORDER BY total_purchase DESC
LIMIT 3;