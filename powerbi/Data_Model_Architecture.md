# Power BI Data Model Architecture & Schema Design
**Project:** Cart Abandonment Pattern Analysis  
**Role:** Senior Data Analyst  

---

## 1. Dimensional Star Schema Architecture

To deliver sub-second interactive query performance across millions of transaction rows, the data model follows a classic **Star Schema** architecture:

```
                  ┌──────────────────────────────┐
                  │      Dim_Date / Dim_Time     │
                  │  (Date, DayOfWeek, Hour,     │
                  │   TimeBucket, Month, Year)   │
                  └──────────────┬───────────────┘
                                 │ 1
                                 │ 
                                 │ *
┌─────────────────────────┐      │      ┌─────────────────────────┐
│       Dim_Device        │      │      │      Dim_Category       │
│  (DeviceType, Category) ├──────┼──────┤  (CategoryCode, Dept,   │
└────────────┬────────────┘      │      │   SubCategory, CategoryID)
             │ 1                 │      └────────────┬────────────┘
             │                   │                   │ 1
             │ *                 ▼ *                 │ *
        ┌────┴───────────────────────────────────────┴────┐
        │                 Fact_CartEvents                 │
        │  (event_time, order_id, product_id, price,      │
        │   cart_value, checkout_step, customer_type,     │
        │   abandoned_flag, interaction_count)            │
        └────────────────────────┬────────────────────────┘
                                 │ *
                                 │ 
                                 │ 1
                  ┌──────────────┴───────────────┐
                  │         Dim_Customer         │
                  │  (user_id, customer_type,    │
                  │   first_order_id, cohort)    │
                  └──────────────────────────────┘
```

---

## 2. Table Specifications & Relationships

### `Fact_CartEvents` (Central Fact Table)
- **Granularity:** One record per cart item interaction.
- **Key Columns:**
  - `event_time` (FK -> `Dim_Date`)
  - `order_id` (Degenerate dimension / Order identifier)
  - `user_id` (FK -> `Dim_Customer`)
  - `category_code` (FK -> `Dim_Category`)
  - `device_type_simulated` (FK -> `Dim_Device`)
  - `checkout_step` (Funnel stage reached)
  - `customer_type` (New / Returning / Anonymous)
  - `price` (Line item price, USD)
  - `cart_value` (Aggregated order cart value, USD)
  - `abandoned_flag` (1 = Abandoned, 0 = Completed)

### `Dim_Date` / `Dim_Time`
- **Granularity:** Day and Hour.
- **Attributes:** `DateKey`, `FullDate`, `DayOfWeek`, `DayOfWeekNumber`, `Hour` (0-23), `TimeBucket` (Morning, Afternoon, Evening, Night), `IsWeekend`.

### `Dim_Device`
- **Granularity:** Device type.
- **Attributes:** `DeviceType` (Mobile, Desktop, Tablet), `FormFactorCategory`.

### `Dim_Category`
- **Granularity:** Product taxonomy code.
- **Attributes:** `CategoryCode`, `SuperCategory` (e.g. appliances, computers, apparel), `SubCategory`.

### `Dim_Customer`
- **Granularity:** Unique user account.
- **Attributes:** `UserID`, `CustomerType` (New, Returning, Anonymous), `FirstOrderDate`.

---

## 3. Storage Mode & Refresh Strategy
- **Recommended Mode:** Import Mode (via Power BI Desktop or Service) with incremental refresh on `event_time`.
- **VertiPaq Optimization:**
  - `order_id` and `product_id` set to BigInt.
  - Disable Auto Date/Time in Power BI Options to save 30% memory.
  - Sorted by `event_time` ascending to maximize run-length encoding (RLE) compression.
