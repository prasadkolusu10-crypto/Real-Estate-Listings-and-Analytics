CREATE OR REPLACE VIEW HighDemandAreas AS
SELECT 
    p.city,
    p.state,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(AVG(t.sale_price), 2) AS avg_sale_price,
    MIN(t.sale_date) AS first_sale,
    MAX(t.sale_date) AS latest_sale
FROM 
    Properties p
    INNER JOIN Transactions t ON p.property_id = t.property_id
GROUP BY 
    p.city, p.state
HAVING 
    transaction_count >= 2  
ORDER BY 
    transaction_count DESC, avg_sale_price DESC;