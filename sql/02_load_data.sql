-- ============================================================================
-- CART ABANDONMENT PATTERN ANALYSIS - POSTGRESQL DATA LOADING
-- Author: Senior Data Analyst
-- Description: Ingesting data/kz_clean.csv into PostgreSQL table cart_events
-- ============================================================================

-- Method 1: Direct SQL COPY (Run in pgAdmin Query Tool)
COPY cart_events
FROM 'C:/Users/anmol/OneDrive/Desktop/cart project/data/kz_clean.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Verification Queries after Loading:
SELECT 
    COUNT(*) AS total_rows_loaded,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(DISTINCT user_id) AS distinct_users,
    MIN(event_time) AS earliest_event,
    MAX(event_time) AS latest_event
FROM cart_events;

-- Check distribution of checkout steps:
SELECT 
    checkout_step,
    COUNT(*) AS row_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_distribution
FROM cart_events
GROUP BY checkout_step
ORDER BY row_count DESC;
