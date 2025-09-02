create OR replace VIEW HighDemandAreas AS
select 
    p.city,
    p.state,
    COUNT(t.transaction_id) AS transaction_count,
    AVG(t.sale_price) AS avg_sale_price
FROM Properties p
JOIN Transactions t ON p.property_id = t.property_id
GROUP BY p.city, p.state
HAVING transaction_count >= 2
ORDER BY transaction_count DESC;