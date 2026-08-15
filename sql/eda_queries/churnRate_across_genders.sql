-- Q1: Which customer profiles have the highest churn risk rate based on gender?

WITH main_tbl AS (
    SELECT
        gender,
        COUNT(*) AS total_customer,
        SUM(churned::int) AS total_churn
    FROM public.demographic
    GROUP BY gender
)

SELECT
    *,
    TO_CHAR(
        ROUND((total_churn * 100.0 / total_customer)::numeric, 2),
        'FM990.00'
    ) || '%' AS churn_rate
FROM main_tbl
ORDER BY total_churn * 100.0 / total_customer DESC;