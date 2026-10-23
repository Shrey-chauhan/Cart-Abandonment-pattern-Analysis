DROP TABLE IF EXISTS cart_events CASCADE;
DROP VIEW IF EXISTS v_orders_summary CASCADE;

CREATE TABLE cart_events (
    event_time TIMESTAMPTZ NOT NULL,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    category_code VARCHAR(100) DEFAULT 'Unknown',
    brand VARCHAR(100) DEFAULT 'Unknown',
    price NUMERIC(10, 2) NOT NULL,
    user_id BIGINT NOT NULL DEFAULT 0,
    hour SMALLINT NOT NULL CHECK (hour BETWEEN 0 AND 23),
    day_of_week VARCHAR(15) NOT NULL,
    time_bucket VARCHAR(20) NOT NULL,
    cart_value NUMERIC(12, 2) NOT NULL,
    interaction_count INT NOT NULL,
    checkout_step VARCHAR(30) NOT NULL,
    device_type_simulated VARCHAR(20) NOT NULL,
    first_order_id VARCHAR(50),
    customer_type VARCHAR(20) NOT NULL,
    abandoned_flag SMALLINT NOT NULL CHECK (abandoned_flag IN (0, 1))
);

CREATE INDEX idx_cart_events_order_id ON cart_events(order_id);
CREATE INDEX idx_cart_events_user_id ON cart_events(user_id);
CREATE INDEX idx_cart_events_checkout_step ON cart_events(checkout_step);
CREATE INDEX idx_cart_events_device ON cart_events(device_type_simulated);
CREATE INDEX idx_cart_events_abandoned ON cart_events(abandoned_flag);
COPY cart_events
FROM 'C:/Users/Public/kz_clean.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',');
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS distinct_orders,
    ROUND(SUM(abandoned_flag) * 100.0 / COUNT(*), 2) AS abandonment_rate_pct
FROM cart_events;

-- Business question
Target Questions: 
--   1. Overall cart abandonment rate (%)
--   2. Drop-off rate at each checkout step (Funnel Analysis)
--   3. Abandonment rate by device type
--   4. Top 10 product categories with highest abandonment
--   5. Abandonment by hour of day (identifying peak abandonment window)
--   6. Abandonment by day of week
--   7. New vs Returning customer abandonment comparison
--   8. Total estimated revenue lost to abandoned carts
--   9. Average Cart Value of abandoned vs completed orders
--  10. High-risk multi-dimensional segment analysis
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Overall Cart Abandonment Rate
-- Purpose: Executive KPI for overall checkout abandonment at the distinct order level
-- ----------------------------------------------------------------------------
WITH distinct_orders AS (
    SELECT 
        order_id,
        MIN(abandoned_flag) AS is_abandoned
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    COUNT(*) AS total_orders,
    SUM(CASE WHEN is_abandoned = 1 THEN 1 ELSE 0 END) AS abandoned_orders,
    SUM(CASE WHEN is_abandoned = 0 THEN 1 ELSE 0 END) AS completed_orders,
    ROUND(SUM(CASE WHEN is_abandoned = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS abandonment_rate_pct,
    ROUND(SUM(CASE WHEN is_abandoned = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS completion_rate_pct
FROM distinct_orders;


-- ----------------------------------------------------------------------------
-- QUERY 2: Checkout Funnel Drop-off Analysis
-- Purpose: Track volume and drop-off rate step-by-step from Cart to Confirmation
-- ----------------------------------------------------------------------------
WITH step_counts AS (
    SELECT 
        checkout_step,
        COUNT(DISTINCT order_id) AS orders_reached,
        CASE checkout_step
            WHEN 'Cart' THEN 1
            WHEN 'Login/Address' THEN 2
            WHEN 'Shipping' THEN 3
            WHEN 'Payment' THEN 4
            WHEN 'Order Confirmation' THEN 5
        END AS step_order
    FROM cart_events
    GROUP BY checkout_step
)
SELECT 
    checkout_step,
    orders_reached,
    LAG(orders_reached) OVER (ORDER BY step_order) AS previous_step_orders,
    LAG(orders_reached) OVER (ORDER BY step_order) - orders_reached AS dropped_at_stage,
    ROUND(
        (LAG(orders_reached) OVER (ORDER BY step_order) - orders_reached) * 100.0 / 
        LAG(orders_reached) OVER (ORDER BY step_order), 2
    ) AS step_drop_off_pct,
    ROUND(
        orders_reached * 100.0 / FIRST_VALUE(orders_reached) OVER (ORDER BY step_order), 2
    ) AS cumulative_conversion_pct
FROM step_counts
ORDER BY step_order;


-- ----------------------------------------------------------------------------
-- QUERY 3: Abandonment Rate & Revenue Impact by Device Type
-- Purpose: Identify if mobile or desktop users suffer worse UX drop-offs
-- ----------------------------------------------------------------------------
WITH device_orders AS (
    SELECT 
        order_id,
        MIN(device_type_simulated) AS device_type,
        MIN(abandoned_flag) AS is_abandoned,
        MIN(cart_value) AS cart_value
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    device_type,
    COUNT(*) AS total_orders,
    SUM(is_abandoned) AS abandoned_orders,
    ROUND(SUM(is_abandoned) * 100.0 / COUNT(*), 2) AS abandonment_rate_pct,
    ROUND(AVG(cart_value), 2) AS avg_cart_value,
    ROUND(SUM(CASE WHEN is_abandoned = 1 THEN cart_value ELSE 0 END), 2) AS estimated_lost_revenue
FROM device_orders
GROUP BY device_type
ORDER BY estimated_lost_revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 4: Top 10 Product Categories with Highest Abandonment Rate
-- Purpose: Spot category-specific friction, pricing hesitation, or sizing doubts
-- ----------------------------------------------------------------------------
WITH category_metrics AS (
    SELECT 
        category_code,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT CASE WHEN abandoned_flag = 1 THEN order_id END) AS abandoned_orders,
        ROUND(AVG(price), 2) AS avg_item_price
    FROM cart_events
    WHERE category_code <> 'Unknown'
    GROUP BY category_code
)
SELECT 
    category_code,
    total_orders,
    abandoned_orders,
    ROUND(abandoned_orders * 100.0 / total_orders, 2) AS abandonment_rate_pct,
    avg_item_price
FROM category_metrics
WHERE total_orders >= 100  -- Filter out low-sample noise
ORDER BY abandonment_rate_pct DESC, total_orders DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- QUERY 5: Hourly Abandonment Pattern & Peak Risk Window
-- Purpose: Identify peak abandonment hours to schedule re-engagement automations
-- ----------------------------------------------------------------------------
WITH hourly_orders AS (
    SELECT 
        order_id,
        MIN(hour) AS hour_of_day,
        MIN(time_bucket) AS time_bucket,
        MIN(abandoned_flag) AS is_abandoned
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    hour_of_day,
    time_bucket,
    COUNT(*) AS total_orders,
    SUM(is_abandoned) AS abandoned_orders,
    ROUND(SUM(is_abandoned) * 100.0 / COUNT(*), 2) AS hourly_abandonment_rate_pct,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS share_of_daily_volume_pct
FROM hourly_orders
GROUP BY hour_of_day, time_bucket
ORDER BY hour_of_day ASC;


-- ----------------------------------------------------------------------------
-- QUERY 6: Day of Week Abandonment Pattern
-- Purpose: Uncover weekday vs weekend consumer checkout psychology
-- ----------------------------------------------------------------------------
WITH dow_orders AS (
    SELECT 
        order_id,
        MIN(day_of_week) AS day_of_week,
        MIN(abandoned_flag) AS is_abandoned,
        CASE MIN(day_of_week)
            WHEN 'Monday' THEN 1
            WHEN 'Tuesday' THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4
            WHEN 'Friday' THEN 5
            WHEN 'Saturday' THEN 6
            WHEN 'Sunday' THEN 7
        END AS dow_sort
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    day_of_week,
    COUNT(*) AS total_orders,
    SUM(is_abandoned) AS abandoned_orders,
    ROUND(SUM(is_abandoned) * 100.0 / COUNT(*), 2) AS abandonment_rate_pct
FROM dow_orders
GROUP BY day_of_week, dow_sort
ORDER BY dow_sort;


-- ----------------------------------------------------------------------------
-- QUERY 7: Customer Type Comparison (New vs Returning vs Anonymous)
-- Purpose: Analyze friction differences across user loyalty tiers
-- ----------------------------------------------------------------------------
WITH customer_orders AS (
    SELECT 
        order_id,
        MIN(customer_type) AS customer_type,
        MIN(abandoned_flag) AS is_abandoned,
        MIN(cart_value) AS cart_value
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    customer_type,
    COUNT(*) AS total_orders,
    SUM(is_abandoned) AS abandoned_orders,
    ROUND(SUM(is_abandoned) * 100.0 / COUNT(*), 2) AS abandonment_rate_pct,
    ROUND(AVG(cart_value), 2) AS avg_cart_value,
    ROUND(SUM(CASE WHEN is_abandoned = 1 THEN cart_value ELSE 0 END), 2) AS total_lost_revenue
FROM customer_orders
GROUP BY customer_type
ORDER BY total_orders DESC;


-- ----------------------------------------------------------------------------
-- QUERY 8: Financial Loss Impact: Total Lost Revenue & Loss by Funnel Step
-- Purpose: Quantify the monetary size of the checkout leak
-- ----------------------------------------------------------------------------
WITH order_financials AS (
    SELECT 
        order_id,
        MIN(checkout_step) AS checkout_step,
        MIN(abandoned_flag) AS is_abandoned,
        MIN(cart_value) AS cart_value
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    checkout_step,
    COUNT(*) AS abandoned_order_count,
    ROUND(SUM(cart_value), 2) AS total_lost_revenue_usd,
    ROUND(AVG(cart_value), 2) AS avg_abandoned_cart_value,
    ROUND(SUM(cart_value) * 100.0 / SUM(SUM(cart_value)) OVER(), 2) AS pct_of_total_lost_revenue
FROM order_financials
WHERE is_abandoned = 1
GROUP BY checkout_step
ORDER BY total_lost_revenue_usd DESC;


-- ----------------------------------------------------------------------------
-- QUERY 9: Price Sensitivity: Abandoned vs Completed Orders Comparison
-- Purpose: Determine whether high cart value correlates with increased abandonment
-- ----------------------------------------------------------------------------
WITH order_stats AS (
    SELECT 
        order_id,
        MIN(abandoned_flag) AS is_abandoned,
        MIN(cart_value) AS cart_value,
        COUNT(product_id) AS items_in_cart
    FROM cart_events
    GROUP BY order_id
)
SELECT 
    CASE WHEN is_abandoned = 1 THEN 'Abandoned Orders' ELSE 'Completed Orders' END AS order_status,
    COUNT(*) AS order_count,
    ROUND(AVG(cart_value), 2) AS mean_cart_value,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cart_value)::NUMERIC, 2) AS median_cart_value,
    ROUND(AVG(items_in_cart), 2) AS avg_items_per_order,
    ROUND(SUM(cart_value), 2) AS total_monetary_value
FROM order_stats
GROUP BY is_abandoned;


-- ----------------------------------------------------------------------------
-- QUERY 10: Multi-Dimensional High-Risk Cohort Segmentation
-- Purpose: Actionable targeting matrix (Device + Category + Customer Type)
-- ----------------------------------------------------------------------------
WITH segmented_orders AS (
    SELECT 
        order_id,
        MIN(device_type_simulated) AS device_type,
        MIN(customer_type) AS customer_type,
        MIN(category_code) AS category_code,
        MIN(abandoned_flag) AS is_abandoned,
        MIN(cart_value) AS cart_value
    FROM cart_events
    WHERE category_code <> 'Unknown'
    GROUP BY order_id
)
SELECT 
    device_type,
    customer_type,
    category_code,
    COUNT(*) AS segment_orders,
    SUM(is_abandoned) AS abandoned_orders,
    ROUND(SUM(is_abandoned) * 100.0 / COUNT(*), 2) AS abandonment_rate_pct,
    ROUND(SUM(CASE WHEN is_abandoned = 1 THEN cart_value ELSE 0 END), 2) AS segment_lost_revenue
FROM segmented_orders
GROUP BY device_type, customer_type, category_code
HAVING COUNT(*) >= 50
ORDER BY segment_lost_revenue DESC
LIMIT 15;



