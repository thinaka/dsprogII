SELECT product_name, price
FROM products
WHERE price = (
                SELECT MAX(price) 
                FROM products
                WHERE category = 'Electronics'
              )