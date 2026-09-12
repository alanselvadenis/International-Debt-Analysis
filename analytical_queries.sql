USE international_debt_db;

-- =============================================
-- BASIC QUERIES
-- =============================================
-- 1. Retrieve all distinct country names
SELECT DISTINCT country_name FROM countries;

-- 2. Count total number of countries
SELECT COUNT(DISTINCT country_code) AS total_countries FROM countries;

-- 3. Find total number of indicators
SELECT COUNT(DISTINCT indicator_code) AS total_indicators FROM indicators;

-- 4. Display first 10 records
SELECT c.country_name, i.indicator_name, d.debt 
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
JOIN indicators i ON d.indicator_code = i.indicator_code
LIMIT 10;

-- 5. Total global debt
SELECT SUM(debt) AS total_global_debt FROM international_debt;

-- 6. Unique indicator names
SELECT DISTINCT indicator_name FROM indicators;

-- 7. Record count per country
SELECT country_code, COUNT(*) AS record_count FROM international_debt GROUP BY country_code;

-- 8. Records where debt > 1 Billion USD
SELECT * FROM international_debt WHERE debt > 1000000000;

-- 9. Min, Max, and Average debt
SELECT MIN(debt) AS min_debt, MAX(debt) AS max_debt, AVG(debt) AS avg_debt FROM international_debt;

-- 10. Total records count
SELECT COUNT(*) AS total_records FROM international_debt;


-- =============================================
-- INTERMEDIATE QUERIES
-- =============================================
-- 11. Total debt per country
SELECT c.country_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name;

-- 12. Top 10 countries with highest total debt
SELECT c.country_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name ORDER BY total_debt DESC LIMIT 10;

-- 13. Average debt per country
SELECT c.country_name, AVG(d.debt) AS avg_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name;

-- 14. Total debt for each indicator
SELECT i.indicator_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN indicators i ON d.indicator_code = i.indicator_code
GROUP BY i.indicator_name;

-- 15. Indicator contributing highest total debt
SELECT i.indicator_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN indicators i ON d.indicator_code = i.indicator_code
GROUP BY i.indicator_name ORDER BY total_debt DESC LIMIT 1;

-- 16. Country with lowest total debt
SELECT c.country_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name ORDER BY total_debt ASC LIMIT 1;

-- 17. Total debt per country & indicator combination
SELECT c.country_name, i.indicator_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
JOIN indicators i ON d.indicator_code = i.indicator_code
GROUP BY c.country_name, i.indicator_name;

-- 18. Count of indicators per country
SELECT c.country_name, COUNT(DISTINCT d.indicator_code) AS indicator_count
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name;

-- 19. Countries with total debt above global average
SELECT c.country_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name
HAVING total_debt > (SELECT AVG(debt) FROM international_debt);

-- 20. Rank countries based on total debt
SELECT c.country_name, SUM(d.debt) AS total_debt,
       DENSE_RANK() OVER (ORDER BY SUM(d.debt) DESC) AS debt_rank
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name;


-- =============================================
-- ADVANCED QUERIES
-- =============================================
-- 21. Top 5 indicators contributing most to global debt
SELECT i.indicator_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN indicators i ON d.indicator_code = i.indicator_code
GROUP BY i.indicator_name ORDER BY total_debt DESC LIMIT 5;

-- 22. Percentage contribution of each country to global debt
SELECT c.country_name, SUM(d.debt) AS country_debt,
       (SUM(d.debt) / (SELECT SUM(debt) FROM international_debt) * 100) AS pct_contribution
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name ORDER BY pct_contribution DESC;


-- 23. Top 3 countries for each indicator
WITH RankedDebt AS (
    SELECT i.indicator_name, c.country_name, d.debt,
           ROW_NUMBER() OVER (PARTITION BY d.indicator_code ORDER BY d.debt DESC) as rank_no
    FROM international_debt d
    JOIN countries c ON d.country_code = c.country_code
    JOIN indicators i ON d.indicator_code = i.indicator_code
)
SELECT indicator_name, country_name, debt FROM RankedDebt WHERE rank_no <= 3;

USE international_debt_db;
-- 24. Difference between Max and Min debt per country
SELECT c.country_name, (MAX(d.debt) - MIN(d.debt)) AS debt_range
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name;

USE international_debt_db;
-- 25. Create View for Top 10 Countries by Highest Debt
CREATE OR REPLACE VIEW view_top_10_debt_countries AS
SELECT c.country_name, SUM(d.debt) AS total_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name ORDER BY total_debt DESC LIMIT 10;

USE international_debt_db;
-- 26. Categorize countries into High, Medium, Low Debt
SELECT c.country_name, SUM(d.debt) AS total_debt,
       CASE 
           WHEN SUM(d.debt) > 100000000000 THEN 'High Debt'
           WHEN SUM(d.debt) BETWEEN 10000000000 AND 100000000000 THEN 'Medium Debt'
           ELSE 'Low Debt'
       END AS debt_category
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name;

USE international_debt_db;
-- 27. Cumulative debt per country using window functions
SELECT c.country_name, d.indicator_code, d.debt,
SUM(d.debt) OVER (PARTITION BY d.country_code ORDER BY d.debt DESC) AS cumulative_debt
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code;

USE international_debt_db;
-- 28. Indicators where average debt > overall average debt
SELECT i.indicator_name, AVG(d.debt) AS avg_indicator_debt
FROM international_debt d
JOIN indicators i ON d.indicator_code = i.indicator_code
GROUP BY i.indicator_name
HAVING AVG(d.debt) > (SELECT AVG(debt) FROM international_debt);

USE international_debt_db;
-- 29. Countries contributing > 5% of global debt
SELECT c.country_name, 
       (SUM(d.debt) / (SELECT SUM(debt) FROM international_debt) * 100) AS pct_share
FROM international_debt d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name
HAVING pct_share > 5;

USE international_debt_db;
-- 30. Dominant indicator for each country
WITH CountryIndicators AS (
    SELECT c.country_name, i.indicator_name, d.debt,
           ROW_NUMBER() OVER (PARTITION BY c.country_code ORDER BY d.debt DESC) as rn
    FROM international_debt d
    JOIN countries c ON d.country_code = c.country_code
    JOIN indicators i ON d.indicator_code = i.indicator_code
)
SELECT country_name, indicator_name AS dominant_indicator, debt
FROM CountryIndicators WHERE rn = 1;