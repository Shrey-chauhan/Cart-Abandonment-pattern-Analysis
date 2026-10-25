import pandas as pd
import numpy as np
import os

print('='*60)
print('  PRE-INTERVIEW DATA AUDIT')
print('='*60)

# ── kz.csv ──────────────────────────────────────────────────
print('\n[1] kz.csv (RAW DATA)')
raw = pd.read_csv(r'data/kz.csv')
print(f'  Rows          : {len(raw):,}')
print(f'  Columns       : {len(raw.columns)} -> {list(raw.columns)}')
print(f'  Nulls per col :\n{raw.isnull().sum().to_string()}')

# ── kz_clean.csv ─────────────────────────────────────────────
print('\n[2] kz_clean.csv (CLEANED DATA)')
df = pd.read_csv(r'data/kz_clean.csv')
print(f'  Rows          : {len(df):,}')
print(f'  Columns       : {len(df.columns)} -> {list(df.columns)}')
print(f'  Nulls total   : {df.isnull().sum().sum()}')
print(f'  Abandonment % : {df["abandoned_flag"].mean()*100:.2f}%')
print(f'  Abandoned rows: {(df["abandoned_flag"]==1).sum():,}')
print(f'  Completed rows: {(df["abandoned_flag"]==0).sum():,}')
print(f'  Avg cart value: ${df["cart_value"].mean():.2f}')
print(f'  Price range   : ${df["price"].min():.2f} - ${df["price"].max():.2f}')

print(f'\n  Checkout steps:')
for k, v in df['checkout_step'].value_counts().items():
    print(f'    {k}: {v:,}')

print(f'\n  Device types:')
for k, v in df['device_type_simulated'].value_counts().items():
    print(f'    {k}: {v:,} ({v/len(df)*100:.1f}%)')

print(f'\n  Customer types:')
for k, v in df['customer_type'].value_counts().items():
    print(f'    {k}: {v:,} ({v/len(df)*100:.1f}%)')

print(f'\n  Time buckets:')
for k, v in df['time_bucket'].value_counts().items():
    print(f'    {k}: {v:,}')

# ── Revenue ───────────────────────────────────────────────────
print('\n[3] REVENUE METRICS')
orders   = df.drop_duplicates('order_id')
realized = orders[orders['abandoned_flag']==0]['cart_value'].sum()
lost     = orders[orders['abandoned_flag']==1]['cart_value'].sum()
total    = realized + lost
print(f'  Total unique orders : {len(orders):,}')
print(f'  Realized Revenue    : ${realized:,.0f}')
print(f'  Lost Revenue (GMV)  : ${lost:,.0f}')
print(f'  Total Potential GMV : ${total:,.0f}')
print(f'  Avg Abandoned Cart  : ${orders[orders["abandoned_flag"]==1]["cart_value"].mean():.2f}')
print(f'  Avg Completed Cart  : ${orders[orders["abandoned_flag"]==0]["cart_value"].mean():.2f}')

# ── File Existence ────────────────────────────────────────────
print('\n[4] FILE EXISTENCE CHECK')
files = [
    'data/kz.csv', 'data/kz_clean.csv',
    'clean_data.py', 'run_eda_and_generate_charts.py', 'build_excel_summary.py',
    'excel/cart_abandonment_summary.xlsx',
    'reports/funnel_analysis.png', 'reports/device_analysis.png',
    'reports/category_analysis.png', 'reports/time_analysis.png',
    'reports/dayofweek_analysis.png', 'reports/customer_type_analysis.png',
    'reports/revenue_analysis.png',
    'sql/01_schema.sql', 'sql/02_load_data.sql', 'sql/03_business_queries.sql',
    'powerbi/DAX_Measures.dax', 'powerbi/Data_Model_Architecture.md', 'powerbi/Dashboard.pbix',
    'notebooks/01_data_inspection.ipynb', 'notebooks/02_data_cleaning.ipynb', 'notebooks/03_eda_analysis.ipynb',
    'README.md', '.gitignore'
]
all_ok = True
for f in files:
    exists = os.path.exists(f)
    if not exists:
        all_ok = False
    print(f'  [{"OK     " if exists else "MISSING"}] {f}')

# ── Deleted Files ─────────────────────────────────────────────
print('\n[5] DELETED FILES VERIFICATION (should all be GONE)')
deleted = [
    'powerbi/Dashboard_Design_Guide.md',
    'reports/Cart_Abandonment_Executive_Report.md',
    'sample_raw_data.py',
    'sql/cart_analysis_sql.sql'
]
for f in deleted:
    gone = not os.path.exists(f)
    if not gone:
        all_ok = False
    print(f'  [{"GONE   " if gone else "STILL EXISTS!!!"}] {f}')

print()
print('='*60)
print(f'  AUDIT RESULT: {"✅ ALL GOOD - READY FOR INTERVIEW!" if all_ok else "❌ ISSUES FOUND - CHECK ABOVE"}')
print('='*60)
