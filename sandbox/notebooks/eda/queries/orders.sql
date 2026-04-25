-- Preview
SELECT *
FROM raw.v_bronze_order
limit 5;

-- Aggregation
SELECT order_instrument_name
, count(1) as order_count
, round(min(price::NUMERIC), 2) as min_price
, round(max(price::NUMERIC), 2) as max_price
, round(avg(price::NUMERIC), 2) as avg_price
, round(avg(order_value::NUMERIC), 2) as avg_order_value
, round(avg(order_filled_value::NUMERIC), 2) as avg_filled_value
, round(avg(quantity::NUMERIC), 2) as avg_quantity
FROM raw.v_bronze_order
group by order_instrument_name
order BY avg_order_value DESC


SELECT *
FROM raw.v_bronze_order
WHERE order_instrument_name = 'Vanguard S&P 500 (Dist)'
ORDER BY order_created_at DESC