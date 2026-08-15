-- Q2: Which age groups within each country have churn rates above/below the country average?

WITH main_tbl AS (
    SELECT
        CASE 
            WHEN d.age < 30 THEN 'Under 30'
            WHEN d.age BETWEEN 30 AND 50 THEN 'Between 30-50'
            ELSE 'Above 50'
        END AS age_group,
        d.churned,
        l.geography AS country
    FROM public.demographic d
    JOIN public.location l ON l.locationid = d.locationid
),

second_tbl AS (
    SELECT
        country,
        age_group,
        COUNT(*) AS total_customer,
        AVG(churned::int::float) AS average_churn_rate,
        AVG(AVG(churned::int::float)) OVER (PARTITION BY country) AS average_churn_country
    FROM main_tbl
    GROUP BY country, age_group
)

SELECT
    *,
    average_churn_country - average_churn_rate AS diff
FROM second_tbl
ORDER BY country, age_group;