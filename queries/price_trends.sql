select 
    city,
    sale_date,
    sale_price,
    AVG(sale_price) OVER (PARTITION BY city ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3
FROM Transactions t
JOIN Properties p ON t.property_id = p.property_id
ORDER BY city, sale_date;