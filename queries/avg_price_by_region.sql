select 
city,
state,
Avg(price) AS avg_listing_price,
COUNT(*) AS property_count
FROM Properties
GROUP BY city, state
ORDER BY avg_listing_price DESC;