SELECT *
FROM v_bronze_dividend
LIMIT 5

SELECT
	ticker
, instrument_name
, sum(amount::numeric) as total_dividend_paid
, avg(amount::numeric) as avg_dividend_paid
, sum(amountineuro::numeric) as total_dividend_paid_in_euro
, max(amountineuro::numeric) as max_dividend_paid_in_euro
, min(amountineuro::numeric) as min_dividend_paid_in_euro
, max(paid_on) as last_paid_on
, min(paid_on) as first_paid_on
FROM v_bronze_dividend
group by ticker, instrument_name
order by total_dividend_paid desc LIMIT 100

SELECT sum(amount::numeric) as total_dividend_paid
FROM v_bronze_dividend LIMIT 100