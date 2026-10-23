-- ============================================================================
-- CART ABANDONMENT PATTERN ANALYSIS - POSTGRESQL SCHEMA
-- Author: Senior Data Analyst
-- Database: PostgreSQL 12+
-- Description: DDL schema and indexes for clean e-commerce cart abandonment analysis
-- ============================================================================

DROP TABLE IF EXISTS cart_events CASCADE;
DROP VIEW IF EXISTS v_orders_summary CASCADE;

-- 1. Main Events Table (Matches kz_clean.csv columns 1-to-1)
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

-- Performance Indexes for Analytics & Aggregations
CREATE INDEX idx_cart_events_order_id ON cart_events(order_id);
CREATE INDEX idx_cart_events_user_id ON cart_events(user_id);
CREATE INDEX idx_cart_events_checkout_step ON cart_events(checkout_step);
CREATE INDEX idx_cart_events_device ON cart_events(device_type_simulated);
CREATE INDEX idx_cart_events_category ON cart_events(category_code);
CREATE INDEX idx_cart_events_customer_type ON cart_events(customer_type);
CREATE INDEX idx_cart_events_abandoned ON cart_events(abandoned_flag);
CREATE INDEX idx_cart_events_event_time ON cart_events(event_time);

-- 2. Materialized View for Order-Level Analysis (Deduplicated by order_id)
CREATE OR REPLACE VIEW v_orders_summary AS
SELECT 
    order_id,
    MIN(user_id) AS user_id,
    MIN(event_time) AS order_time,
    MIN(hour) AS hour,
    MIN(day_of_week) AS day_of_week,
    MIN(time_bucket) AS time_bucket,
    MIN(device_type_simulated) AS device_type,
    MIN(customer_type) AS customer_type,
    MIN(checkout_step) AS checkout_step,
    MIN(abandoned_flag) AS abandoned_flag,
    COUNT(product_id) AS items_in_cart,
    MIN(cart_value) AS cart_value
FROM cart_events
GROUP BY order_id;

COMMENT ON TABLE cart_events IS 'Contains item-level checkout events matching kz_clean.csv columns exactly.';
COMMENT ON VIEW v_orders_summary IS 'Order-level aggregated view for distinct order funnel & financial abandonment metrics.';
