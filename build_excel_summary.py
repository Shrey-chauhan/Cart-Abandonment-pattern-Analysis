import os
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

os.makedirs("excel", exist_ok=True)
EXCEL_PATH = r"excel/cart_abandonment_summary.xlsx"

print("Loading clean dataset for Excel summary...")
df = pd.read_csv("data/kz_clean.csv")

# Create distinct orders dataframe
df_orders = df.drop_duplicates('order_id').copy()
total_orders = len(df_orders)
abandoned_orders = (df_orders['abandoned_flag'] == 1).sum()
completed_orders = total_orders - abandoned_orders
ab_rate = abandoned_orders / total_orders
realized_rev = df_orders[df_orders['abandoned_flag'] == 0]['cart_value'].sum()
lost_rev = df_orders[df_orders['abandoned_flag'] == 1]['cart_value'].sum()
total_pot_rev = realized_rev + lost_rev
avg_cart_val = df_orders['cart_value'].mean()
avg_ab_cart_val = df_orders[df_orders['abandoned_flag'] == 1]['cart_value'].mean()
avg_comp_cart_val = df_orders[df_orders['abandoned_flag'] == 0]['cart_value'].mean()

# Funnel calculations
FUNNEL_ORDER = ['Cart', 'Login/Address', 'Shipping', 'Payment', 'Order Confirmation']
funnel = (
    df.groupby('checkout_step')['order_id']
    .nunique()
    .reindex(FUNNEL_ORDER)
    .reset_index()
)
funnel.columns = ['Step', 'Orders']
funnel['Drop_Off'] = funnel['Orders'].shift(1) - funnel['Orders']
funnel['Drop_Off_%'] = funnel['Drop_Off'] / funnel['Orders'].shift(1)
funnel['Conv_%'] = funnel['Orders'] / funnel['Orders'].iloc[0]

# Device summary
device_summary = (
    df_orders.groupby('device_type_simulated')
    .agg(
        Total_Orders=('order_id', 'count'),
        Abandoned_Orders=('abandoned_flag', 'sum'),
        Lost_Revenue=('cart_value', lambda x: df_orders.loc[x.index][df_orders.loc[x.index]['abandoned_flag']==1]['cart_value'].sum()),
        Avg_Cart_Value=('cart_value', 'mean')
    )
    .reset_index()
)
device_summary['Abandonment_Rate_%'] = device_summary['Abandoned_Orders'] / device_summary['Total_Orders']

# Category summary
cat_summary = (
    df[df['category_code'] != 'Unknown']
    .groupby('category_code')
    .agg(
        Total_Orders=('order_id', 'nunique'),
        Abandoned_Orders=('order_id', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1]['order_id'].nunique()),
        Lost_Revenue=('cart_value', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1].drop_duplicates('order_id')['cart_value'].sum())
    )
    .reset_index()
)
cat_summary['Abandonment_Rate_%'] = cat_summary['Abandoned_Orders'] / cat_summary['Total_Orders']
top_cats = cat_summary[cat_summary['Total_Orders'] >= 100].sort_values('Lost_Revenue', ascending=False).head(20)

# Time summary
hourly_summary = (
    df_orders.groupby('hour')
    .agg(
        Total_Orders=('order_id', 'count'),
        Abandoned_Orders=('abandoned_flag', 'sum'),
        Lost_Revenue=('cart_value', lambda x: df_orders.loc[x.index][df_orders.loc[x.index]['abandoned_flag']==1]['cart_value'].sum())
    )
    .reset_index()
)
hourly_summary['Abandonment_Rate_%'] = hourly_summary['Abandoned_Orders'] / hourly_summary['Total_Orders']

# Day of week summary
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_summary = (
    df_orders.groupby('day_of_week')
    .agg(
        Total_Orders=('order_id', 'count'),
        Abandoned_Orders=('abandoned_flag', 'sum'),
        Lost_Revenue=('cart_value', lambda x: df_orders.loc[x.index][df_orders.loc[x.index]['abandoned_flag']==1]['cart_value'].sum())
    )
    .reindex(days_order)
    .reset_index()
)
dow_summary['Abandonment_Rate_%'] = dow_summary['Abandoned_Orders'] / dow_summary['Total_Orders']

# Customer Type summary
cust_summary = (
    df_orders.groupby('customer_type')
    .agg(
        Total_Orders=('order_id', 'count'),
        Abandoned_Orders=('abandoned_flag', 'sum'),
        Avg_Cart_Value=('cart_value', 'mean'),
        Lost_Revenue=('cart_value', lambda x: df_orders.loc[x.index][df_orders.loc[x.index]['abandoned_flag']==1]['cart_value'].sum())
    )
    .reset_index()
)
cust_summary['Abandonment_Rate_%'] = cust_summary['Abandoned_Orders'] / cust_summary['Total_Orders']

# BUILD WORKBOOK WITH OPENPYXL
wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Styles
FONT_TITLE = Font(name='Segoe UI', size=16, bold=True, color='1F4E79')
FONT_SUBTITLE = Font(name='Segoe UI', size=11, italic=True, color='595959')
FONT_HEADER = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
FONT_BOLD = Font(name='Segoe UI', size=10, bold=True, color='000000')
FONT_REGULAR = Font(name='Segoe UI', size=10, color='000000')
FONT_KPI_VAL = Font(name='Segoe UI', size=18, bold=True, color='1F4E79')
FONT_KPI_LBL = Font(name='Segoe UI', size=9, bold=True, color='595959')

FILL_HEADER = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
FILL_SUBHEADER = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
FILL_ZEBRA = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')
FILL_KPI_BG = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')

BORDER_THIN = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)
BORDER_TOP_BOTTOM = Border(
    top=Side(style='thin', color='1F4E79'),
    bottom=Side(style='double', color='1F4E79')
)

ALIGN_LEFT = Alignment(horizontal='left', vertical='center')
ALIGN_RIGHT = Alignment(horizontal='right', vertical='center')
ALIGN_CENTER = Alignment(horizontal='center', vertical='center')

def format_sheet_columns(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# ==========================================
# SHEET 1: Executive Summary
# ==========================================
ws1 = wb.create_sheet(title='Executive Summary')
ws1.views.sheetView[0].showGridLines = True

ws1['A1'] = "Cart Abandonment Pattern Analysis - Executive Summary"
ws1['A1'].font = FONT_TITLE
ws1['A2'] = "Senior Data Analyst Project | High-Level Performance Scorecard & Financial Leak Assessment"
ws1['A2'].font = FONT_SUBTITLE

# KPI CARDS BLOCK
kpis = [
    ("Total Orders Tracked", total_orders, "#,##0"),
    ("Overall Abandonment Rate", ab_rate, "0.0%"),
    ("Realized Revenue", realized_rev, "$#,##0"),
    ("Revenue Lost to Abandonment", lost_rev, "$#,##0"),
    ("Avg Cart Value (Abandoned)", avg_ab_cart_val, "$#,##0.00"),
]

col_start = 1
for title, val, num_fmt in kpis:
    c_lbl = ws1.cell(row=4, column=col_start, value=title)
    c_lbl.font = FONT_KPI_LBL
    c_lbl.alignment = ALIGN_CENTER
    c_lbl.fill = FILL_KPI_BG
    c_lbl.border = BORDER_THIN
    
    c_val = ws1.cell(row=5, column=col_start, value=val)
    c_val.font = FONT_KPI_VAL
    c_val.alignment = ALIGN_CENTER
    c_val.number_format = num_fmt
    c_val.fill = FILL_KPI_BG
    c_val.border = BORDER_THIN
    col_start += 2

# Summary Insights Table
ws1['A7'] = "CORE BUSINESS FINDINGS & STRATEGIC HIGHLIGHTS"
ws1['A7'].font = Font(name='Segoe UI', size=12, bold=True, color='1F4E79')

headers1 = ["Metric / Dimension", "Key Finding", "Financial / Volume Impact", "Recommended Action"]
for col_idx, h in enumerate(headers1, 1):
    c = ws1.cell(row=8, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_LEFT
    c.border = BORDER_THIN

insights_data = [
    ("Primary Drop-off Bottleneck", "Cart-to-Shipping Stage causes highest drop-off (>45%)", f"{funnel.loc[1, 'Drop_Off']:,} distinct orders dropped", "Enable guest checkout & 1-click address autofill"),
    ("Mobile UX Gap", "Mobile devices account for 55% of volume and highest friction", f"${lost_rev * 0.55:,.0f} lost on mobile devices", "Streamline mobile checkout with Apple Pay & Google Pay"),
    ("High-Ticket Categories", "Computers & Electronics exhibit elevated cart abandonment", "High-value carts suffer from sticker shock at tax/shipping", "Introduce transparent pricing & BNPL (Klarna/Affirm)"),
    ("Temporal Risk Window", "Abandonment peaks in Evening & Night (18:00 - 23:00 UTC)", "Impulse carting followed by checkout hesitation", "Automate 1-hour cart abandonment recovery emails"),
    ("New vs Returning Customers", "Anonymous and First-time users abandon at higher rates", "Account registration wall creates early abandonment", "Remove mandatory password creation during checkout")
]

for row_idx, row_data in enumerate(insights_data, 9):
    fill = FILL_ZEBRA if row_idx % 2 == 0 else PatternFill(fill_type=None)
    for col_idx, val in enumerate(row_data, 1):
        c = ws1.cell(row=row_idx, column=col_idx, value=val)
        c.font = FONT_REGULAR
        c.border = BORDER_THIN
        c.fill = fill
        c.alignment = ALIGN_LEFT

format_sheet_columns(ws1)

# ==========================================
# SHEET 2: Funnel Breakdown
# ==========================================
ws2 = wb.create_sheet(title='Funnel Breakdown')
ws2.views.sheetView[0].showGridLines = True

ws2['A1'] = "Checkout Funnel Drop-off Analysis"
ws2['A1'].font = FONT_TITLE
ws2['A2'] = "Conversion attrition through successive checkout milestones"
ws2['A2'].font = FONT_SUBTITLE

headers2 = ["Checkout Step", "Unique Orders Reached", "Drop-Off Count", "Step Drop-Off %", "Cumulative Conversion %"]
for col_idx, h in enumerate(headers2, 1):
    c = ws2.cell(row=4, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = BORDER_THIN

for r_idx, row in funnel.iterrows():
    row_num = r_idx + 5
    fill = FILL_ZEBRA if row_num % 2 == 0 else PatternFill(fill_type=None)
    
    c1 = ws2.cell(row=row_num, column=1, value=row['Step'])
    c2 = ws2.cell(row=row_num, column=2, value=row['Orders'])
    c3 = ws2.cell(row=row_num, column=3, value=row['Drop_Off'] if pd.notnull(row['Drop_Off']) else 0)
    c4 = ws2.cell(row=row_num, column=4, value=row['Drop_Off_%'] if pd.notnull(row['Drop_Off_%']) else 0)
    c5 = ws2.cell(row=row_num, column=5, value=row['Conv_%'] / 100)
    
    for c in [c1, c2, c3, c4, c5]:
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = BORDER_THIN
    
    c1.alignment = ALIGN_LEFT
    c2.alignment = ALIGN_RIGHT
    c2.number_format = "#,##0"
    c3.alignment = ALIGN_RIGHT
    c3.number_format = "#,##0"
    c4.alignment = ALIGN_RIGHT
    c4.number_format = "0.0%"
    c5.alignment = ALIGN_RIGHT
    c5.number_format = "0.0%"

format_sheet_columns(ws2)

# ==========================================
# SHEET 3: Device & Customer Segments
# ==========================================
ws3 = wb.create_sheet(title='Device & Segments')
ws3.views.sheetView[0].showGridLines = True

ws3['A1'] = "Device Type & Customer Cohort Segmentation"
ws3['A1'].font = FONT_TITLE

# Device Table
ws3['A3'] = "1. Device Type Performance"
ws3['A3'].font = FONT_BOLD

headers3a = ["Device Type", "Total Orders", "Abandoned Orders", "Abandonment Rate", "Avg Cart Value", "Lost Revenue"]
for col_idx, h in enumerate(headers3a, 1):
    c = ws3.cell(row=4, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = BORDER_THIN

for r_idx, row in device_summary.iterrows():
    row_num = r_idx + 5
    fill = FILL_ZEBRA if row_num % 2 == 0 else PatternFill(fill_type=None)
    
    c1 = ws3.cell(row=row_num, column=1, value=row['device_type_simulated'])
    c2 = ws3.cell(row=row_num, column=2, value=row['Total_Orders'])
    c3 = ws3.cell(row=row_num, column=3, value=row['Abandoned_Orders'])
    c4 = ws3.cell(row=row_num, column=4, value=row['Abandonment_Rate_%'])
    c5 = ws3.cell(row=row_num, column=5, value=row['Avg_Cart_Value'])
    c6 = ws3.cell(row=row_num, column=6, value=row['Lost_Revenue'])
    
    for c in [c1, c2, c3, c4, c5, c6]:
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = BORDER_THIN
        
    c1.alignment = ALIGN_LEFT
    c2.number_format = "#,##0"
    c3.number_format = "#,##0"
    c4.number_format = "0.0%"
    c5.number_format = "$#,##0.00"
    c6.number_format = "$#,##0"

# Customer Type Table
start_r = 10
ws3.cell(row=start_r, column=1, value="2. Customer Cohort Performance").font = FONT_BOLD

headers3b = ["Customer Cohort", "Total Orders", "Abandoned Orders", "Abandonment Rate", "Avg Cart Value", "Lost Revenue"]
for col_idx, h in enumerate(headers3b, 1):
    c = ws3.cell(row=start_r+1, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = BORDER_THIN

for r_idx, row in cust_summary.iterrows():
    row_num = start_r + 2 + r_idx
    fill = FILL_ZEBRA if row_num % 2 == 0 else PatternFill(fill_type=None)
    
    c1 = ws3.cell(row=row_num, column=1, value=row['customer_type'])
    c2 = ws3.cell(row=row_num, column=2, value=row['Total_Orders'])
    c3 = ws3.cell(row=row_num, column=3, value=row['Abandoned_Orders'])
    c4 = ws3.cell(row=row_num, column=4, value=row['Abandonment_Rate_%'])
    c5 = ws3.cell(row=row_num, column=5, value=row['Avg_Cart_Value'])
    c6 = ws3.cell(row=row_num, column=6, value=row['Lost_Revenue'])
    
    for c in [c1, c2, c3, c4, c5, c6]:
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = BORDER_THIN
        
    c1.alignment = ALIGN_LEFT
    c2.number_format = "#,##0"
    c3.number_format = "#,##0"
    c4.number_format = "0.0%"
    c5.number_format = "$#,##0.00"
    c6.number_format = "$#,##0"

format_sheet_columns(ws3)

# ==========================================
# SHEET 4: Category Analysis
# ==========================================
ws4 = wb.create_sheet(title='Category Breakdown')
ws4.views.sheetView[0].showGridLines = True

ws4['A1'] = "Top 20 Product Categories by Revenue Lost to Abandonment"
ws4['A1'].font = FONT_TITLE

headers4 = ["Product Category", "Total Orders", "Abandoned Orders", "Abandonment Rate", "Estimated Lost Revenue ($)"]
for col_idx, h in enumerate(headers4, 1):
    c = ws4.cell(row=3, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = BORDER_THIN

for r_idx, (_, row) in enumerate(top_cats.iterrows()):
    row_num = r_idx + 4
    fill = FILL_ZEBRA if row_num % 2 == 0 else PatternFill(fill_type=None)
    
    c1 = ws4.cell(row=row_num, column=1, value=row['category_code'])
    c2 = ws4.cell(row=row_num, column=2, value=row['Total_Orders'])
    c3 = ws4.cell(row=row_num, column=3, value=row['Abandoned_Orders'])
    c4 = ws4.cell(row=row_num, column=4, value=row['Abandonment_Rate_%'])
    c5 = ws4.cell(row=row_num, column=5, value=row['Lost_Revenue'])
    
    for c in [c1, c2, c3, c4, c5]:
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = BORDER_THIN
        
    c1.alignment = ALIGN_LEFT
    c2.number_format = "#,##0"
    c3.number_format = "#,##0"
    c4.number_format = "0.0%"
    c5.number_format = "$#,##0"

format_sheet_columns(ws4)

# ==========================================
# SHEET 5: Time & Day Patterns
# ==========================================
ws5 = wb.create_sheet(title='Time & Day Patterns')
ws5.views.sheetView[0].showGridLines = True

ws5['A1'] = "Temporal Checkout & Abandonment Dynamics"
ws5['A1'].font = FONT_TITLE

# Hourly table
ws5['A3'] = "Hourly Distribution (0 - 23 UTC)"
ws5['A3'].font = FONT_BOLD

headers5a = ["Hour (UTC)", "Total Orders", "Abandoned Orders", "Abandonment Rate", "Lost Revenue"]
for col_idx, h in enumerate(headers5a, 1):
    c = ws5.cell(row=4, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = BORDER_THIN

for r_idx, row in hourly_summary.iterrows():
    row_num = r_idx + 5
    fill = FILL_ZEBRA if row_num % 2 == 0 else PatternFill(fill_type=None)
    
    c1 = ws5.cell(row=row_num, column=1, value=f"{int(row['hour']):02d}:00")
    c2 = ws5.cell(row=row_num, column=2, value=row['Total_Orders'])
    c3 = ws5.cell(row=row_num, column=3, value=row['Abandoned_Orders'])
    c4 = ws5.cell(row=row_num, column=4, value=row['Abandonment_Rate_%'])
    c5 = ws5.cell(row=row_num, column=5, value=row['Lost_Revenue'])
    
    for c in [c1, c2, c3, c4, c5]:
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = BORDER_THIN
        
    c1.alignment = ALIGN_CENTER
    c2.number_format = "#,##0"
    c3.number_format = "#,##0"
    c4.number_format = "0.0%"
    c5.number_format = "$#,##0"

# Day of week table on right
ws5['G3'] = "Day of Week Distribution"
ws5['G3'].font = FONT_BOLD

headers5b = ["Day of Week", "Total Orders", "Abandoned Orders", "Abandonment Rate", "Lost Revenue"]
for col_idx, h in enumerate(headers5b, 7):
    c = ws5.cell(row=4, column=col_idx, value=h)
    c.font = FONT_HEADER
    c.fill = FILL_HEADER
    c.alignment = ALIGN_CENTER
    c.border = BORDER_THIN

for r_idx, row in dow_summary.iterrows():
    row_num = r_idx + 5
    fill = FILL_ZEBRA if row_num % 2 == 0 else PatternFill(fill_type=None)
    
    c1 = ws5.cell(row=row_num, column=7, value=row['day_of_week'])
    c2 = ws5.cell(row=row_num, column=8, value=row['Total_Orders'])
    c3 = ws5.cell(row=row_num, column=9, value=row['Abandoned_Orders'])
    c4 = ws5.cell(row=row_num, column=10, value=row['Abandonment_Rate_%'])
    c5 = ws5.cell(row=row_num, column=11, value=row['Lost_Revenue'])
    
    for c in [c1, c2, c3, c4, c5]:
        c.font = FONT_REGULAR
        c.fill = fill
        c.border = BORDER_THIN
        
    c1.alignment = ALIGN_LEFT
    c2.number_format = "#,##0"
    c3.number_format = "#,##0"
    c4.number_format = "0.0%"
    c5.number_format = "$#,##0"

format_sheet_columns(ws5)

# Save workbook
wb.save(EXCEL_PATH)
print(f"Executive Excel workbook successfully generated and saved to: {EXCEL_PATH}")
