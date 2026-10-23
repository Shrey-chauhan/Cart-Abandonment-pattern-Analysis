# Power BI Dashboard Blueprint & Visual Layout Guide
**Project:** Cart Abandonment Pattern Analysis  
**Analyst:** Senior Data Analyst  

---

## Executive Summary & Canvas Configuration
- **Canvas Size:** 16:9 widescreen (`1920 x 1080` or `1280 x 720`)
- **Color Theme:** Modern Executive Navy Palette
  - **Primary:** Dark Navy (`#1F4E79`)
  - **Warning / Attrition:** Coral Red (`#E15759`)
  - **Success / Conversion:** Emerald Green (`#59A14F`)
  - **Neutral / Accent:** Slate Gray (`#76B7B2`, `#D9E1F2`, `#F2F5F9`)
  - **Background:** Clean Soft Off-White (`#F8F9FA`) with white card containers (`#FFFFFF`, subtle 2px drop-shadow)

---

## Page Architecture (4 Interactive Tabs)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PAGE 1: EXECUTIVE KPI & REVENUE LEAK                  │
│  [Top Slicers: Date Range | Device Type | Customer Type | Product Category]  │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Card 1]            [Card 2]           [Card 3]            [Card 4]        │
│  Total Orders        Abandonment Rate   Realized Revenue    Lost Revenue    │
│  514,281             82.4%              $48.2M              $226.5M         │
├───────────────────────────────────────┬─────────────────────────────────────┤
│  [Visual 1: Donut Chart]              │  [Visual 2: Clustered Bar]          │
│  Realized vs Lost Revenue Share       │  Lost Revenue by Funnel Stage       │
│  (Green vs Red breakdown)             │  (Cart -> Address -> Shipping)      │
├───────────────────────────────────────┴─────────────────────────────────────┤
│  [Visual 3: Ribbon / Area Trend]                                            │
│  Daily Abandonment Rate & Volume Over Time                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Page 1: Executive KPI & Revenue Leak Overview
1. **Top Navigation & Slicers Bar:**
   - Date Range Slider (`event_time`)
   - Device Type Dropdown (`device_type_simulated`)
   - Customer Segment Button Bar (`New`, `Returning`, `Anonymous`)
   - Product Category Search Bar
2. **Key Metric KPI Cards (Top Row):**
   - **Card 1: Total Orders:** `[Total Orders]` formatted as `#,##0`.
   - **Card 2: Cart Abandonment Rate:** `[Abandonment Rate]` with red conditional callout.
   - **Card 3: Realized Revenue:** `[Realized Revenue]` formatted as `$#,##0`.
   - **Card 4: Revenue Lost to Abandonment:** `[Lost Revenue]` formatted as `$#,##0`.
   - **Card 5: Recovery Opportunity (5%):** `[Recoverable Revenue (5% Lift)]` highlighted in gold.
3. **Primary Charts:**
   - **Donut Chart:** Realized Revenue ($) vs Lost Revenue ($).
   - **Horizontal Bar Chart:** Estimated Lost Revenue ($) by Checkout Drop-off Stage.
   - **Time Series Line Chart:** Abandonment Rate % trend line overlaid on daily order volume bars.

---

### Page 2: Funnel Drop-off Deep-Dive
1. **Funnel Visualization:**
   - Stages: `Cart` -> `Login/Address` -> `Shipping` -> `Payment` -> `Order Confirmation`
   - Bars showing unique orders at each stage with data labels.
2. **Drop-Off Waterfall Chart:**
   - Visualizing the volume leaking at each stage:
     - Stage 1 to 2 (Cart to Address): -X orders
     - Stage 2 to 3 (Address to Shipping): -Y orders
     - Stage 3 to 4 (Shipping to Payment): -Z orders
     - Stage 4 to 5 (Payment to Confirmation): Final completed
3. **Friction Diagnostic Table:**
   - Columns: Checkout Step, Orders Reached, Drop-off Volume, Step Drop-off %, Revenue Leaked.

---

### Page 3: Customer & Segment Analysis (Device, Category, Loyalty)
1. **Device Comparison Matrix:**
   - Mobile vs Desktop vs Tablet side-by-side gauge cards for Abandonment Rate.
   - Bar chart of Average Cart Value across devices.
2. **Customer Cohort Heatmap:**
   - Matrix visual: Rows = `Customer Type` (New, Returning, Anonymous), Columns = `Device Type`, Values = `[Abandonment Rate]` with background color gradient.
3. **Category Scatter Plot:**
   - X-Axis: `Average Item Price ($)`
   - Y-Axis: `Abandonment Rate (%)`
   - Bubble Size: `[Lost Revenue]`
   - Tooltip: `Category Code`, `Total Orders`, `Abandoned Orders`.
   - Uncovers high-ticket pricing resistance and category-specific drop-off drivers.

---

### Page 4: Time Pattern & Action Matrix
1. **Hourly Rhythm Heatmap:**
   - 24-Hour column chart highlighting peak shopping vs peak drop-off hours (18:00 - 23:00 UTC).
2. **Day of Week Comparison:**
   - Monday to Sunday conversion performance.
3. **Prioritized Action Matrix Visual:**
   - Interactive table mapping high-impact fixes (e.g. Guest Checkout, Express Payment Buttons, Automated Email Reminders) with estimated revenue upside.
