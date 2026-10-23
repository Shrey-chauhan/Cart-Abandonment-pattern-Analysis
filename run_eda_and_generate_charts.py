import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

os.makedirs("reports", exist_ok=True)

plt.rcParams.update({
    'figure.figsize'  : (13, 6),
    'axes.spines.top' : False,
    'axes.spines.right': False,
    'axes.titlesize'  : 14,
    'axes.titleweight': 'bold',
    'axes.labelsize'  : 11,
    'xtick.labelsize' : 10,
    'ytick.labelsize' : 10,
    'figure.dpi'      : 120,
})

print("Loading data/kz_clean.csv...")
df = pd.read_csv("data/kz_clean.csv")
print(f"Data loaded: {len(df):,} rows")

# 1. FUNNEL ANALYSIS
FUNNEL_ORDER = ['Cart', 'Login/Address', 'Shipping', 'Payment', 'Order Confirmation']
funnel = (
    df.groupby('checkout_step')['order_id']
    .nunique()
    .reindex(FUNNEL_ORDER)
    .reset_index()
)
funnel.columns = ['Step', 'Orders']
funnel['Drop_Off'] = funnel['Orders'].shift(1) - funnel['Orders']
funnel['Drop_Off_%'] = (funnel['Drop_Off'] / funnel['Orders'].shift(1) * 100).round(1)
funnel['Conv_%'] = (funnel['Orders'] / funnel['Orders'].iloc[0] * 100).round(1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
bars = ax1.barh(funnel['Step'][::-1], funnel['Orders'][::-1],
                color=['#2b5c8f','#3b75af','#5193d5','#f28e2b','#e15759'])
ax1.set_xlabel('Unique Orders')
ax1.set_title('Checkout Funnel — Order Count per Step')
for bar, val in zip(bars, funnel['Orders'][::-1]):
    ax1.text(bar.get_width() + max(funnel['Orders'])*0.01, bar.get_y() + bar.get_height()/2,
             f'{val:,}', va='center', fontsize=10, fontweight='bold')

drop_data = funnel.dropna(subset=['Drop_Off_%'])
bars2 = ax2.bar(drop_data['Step'], drop_data['Drop_Off_%'], color='#e15759', width=0.5)
ax2.set_ylabel('Drop-off Rate (%)')
ax2.set_title('Drop-off Rate at Each Step (%)')
ax2.set_ylim(0, 100)
for bar, val in zip(bars2, drop_data['Drop_Off_%']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/funnel_analysis.png', bbox_inches='tight')
plt.close()
print("1. Funnel chart saved.")

# 2. DEVICE TYPE ANALYSIS
device_summary = (
    df.groupby('device_type_simulated')
    .agg(
        Total_Orders=('order_id', 'nunique'),
        Abandoned_Orders=('order_id', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1]['order_id'].nunique()),
        Lost_Revenue=('cart_value', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1].drop_duplicates('order_id')['cart_value'].sum())
    )
    .reset_index()
)
device_summary['Abandonment_Rate_%'] = (device_summary['Abandoned_Orders'] / device_summary['Total_Orders'] * 100).round(2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
palette = {'Mobile':'#e15759', 'Desktop':'#4e79a7', 'Tablet':'#76b7b2'}
bars1 = ax1.bar(device_summary['device_type_simulated'], device_summary['Abandonment_Rate_%'],
                color=[palette[d] for d in device_summary['device_type_simulated']], width=0.45)
ax1.set_title('Abandonment Rate by Device Type (%)')
ax1.set_ylabel('Abandonment Rate (%)')
ax1.set_ylim(0, 100)
for bar, val in zip(bars1, device_summary['Abandonment_Rate_%']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')

bars2 = ax2.bar(device_summary['device_type_simulated'], device_summary['Lost_Revenue'],
                color=[palette[d] for d in device_summary['device_type_simulated']], width=0.45)
ax2.set_title('Estimated Lost Revenue by Device Type ($)')
ax2.set_ylabel('Lost Revenue ($)')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x*1e-6:.1f}M'))
for bar, val in zip(bars2, device_summary['Lost_Revenue']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(device_summary['Lost_Revenue'])*0.01,
             f'${val:,.0f}', ha='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/device_analysis.png', bbox_inches='tight')
plt.close()
print("2. Device chart saved.")

# 3. CATEGORY ANALYSIS
top_cats = (
    df[df['category_code'] != 'Unknown']
    .groupby('category_code')
    .agg(
        Total_Orders=('order_id', 'nunique'),
        Abandoned_Orders=('order_id', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1]['order_id'].nunique()),
        Total_Volume=('order_id', 'count')
    )
    .reset_index()
)
top_cats['Abandonment_Rate_%'] = (top_cats['Abandoned_Orders'] / top_cats['Total_Orders'] * 100).round(2)
top10_worst = top_cats[top_cats['Total_Orders'] >= 100].sort_values('Abandonment_Rate_%', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.barh(top10_worst['category_code'][::-1], top10_worst['Abandonment_Rate_%'][::-1], color='#e15759')
ax.set_title('Top 10 Product Categories by Abandonment Rate (Min 100 Orders)')
ax.set_xlabel('Abandonment Rate (%)')
ax.set_xlim(0, 100)
for bar, val in zip(bars, top10_worst['Abandonment_Rate_%'][::-1]):
    ax.text(bar.get_width() + 1.0, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/category_analysis.png', bbox_inches='tight')
plt.close()
print("3. Category chart saved.")

# 4. TIME OF DAY ANALYSIS
hourly = (
    df.groupby('hour')
    .agg(
        Total_Orders=('order_id', 'nunique'),
        Abandoned_Orders=('order_id', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1]['order_id'].nunique())
    )
    .reset_index()
)
hourly['Abandonment_Rate_%'] = (hourly['Abandoned_Orders'] / hourly['Total_Orders'] * 100).round(2)

fig, ax1 = plt.subplots(figsize=(14, 5))
ax2 = ax1.twinx()
ax1.bar(hourly['hour'], hourly['Total_Orders'], color='#4e79a7', alpha=0.35, label='Total Orders')
ax2.plot(hourly['hour'], hourly['Abandonment_Rate_%'], color='#e15759', marker='o', linewidth=2.5, label='Abandonment Rate %')
ax1.set_xlabel('Hour of Day (0 - 23 UTC)')
ax1.set_ylabel('Total Orders', color='#4e79a7')
ax2.set_ylabel('Abandonment Rate (%)', color='#e15759')
ax1.set_xticks(range(0, 24))
ax1.set_title('Order Volume vs Abandonment Rate by Hour of Day')
plt.tight_layout()
plt.savefig('reports/time_analysis.png', bbox_inches='tight')
plt.close()
print("4. Time chart saved.")

# 5. DAY OF WEEK ANALYSIS
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow = (
    df.groupby('day_of_week')
    .agg(
        Total_Orders=('order_id', 'nunique'),
        Abandoned_Orders=('order_id', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1]['order_id'].nunique())
    )
    .reindex(days_order)
    .reset_index()
)
dow['Abandonment_Rate_%'] = (dow['Abandoned_Orders'] / dow['Total_Orders'] * 100).round(2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
ax1.bar(dow['day_of_week'], dow['Total_Orders'], color='#4e79a7', width=0.5)
ax1.set_title('Order Volume by Day of Week')
ax1.set_ylabel('Total Orders')
ax1.tick_params(axis='x', rotation=30)

ax2.plot(dow['day_of_week'], dow['Abandonment_Rate_%'], color='#e15759', marker='s', linewidth=2.5, markersize=7)
ax2.set_title('Abandonment Rate by Day of Week (%)')
ax2.set_ylabel('Abandonment Rate (%)')
ax2.tick_params(axis='x', rotation=30)
for x, y in zip(dow['day_of_week'], dow['Abandonment_Rate_%']):
    ax2.text(x, y + 0.5, f'{y:.1f}%', ha='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/dayofweek_analysis.png', bbox_inches='tight')
plt.close()
print("5. Day of week chart saved.")

# 6. CUSTOMER TYPE ANALYSIS
cust = (
    df.groupby('customer_type')
    .agg(
        Total_Orders=('order_id', 'nunique'),
        Abandoned_Orders=('order_id', lambda x: df.loc[x.index][df.loc[x.index]['abandoned_flag']==1]['order_id'].nunique()),
        Avg_Cart_Value=('cart_value', 'mean')
    )
    .reset_index()
)
cust['Abandonment_Rate_%'] = (cust['Abandoned_Orders'] / cust['Total_Orders'] * 100).round(2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
bars1 = ax1.bar(cust['customer_type'], cust['Abandonment_Rate_%'], color=['#76b7b2','#4e79a7','#f28e2b'], width=0.45)
ax1.set_title('Abandonment Rate by Customer Type (%)')
ax1.set_ylabel('Abandonment Rate (%)')
ax1.set_ylim(0, 100)
for bar, val in zip(bars1, cust['Abandonment_Rate_%']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5, f'{val:.1f}%', ha='center', fontweight='bold')

bars2 = ax2.bar(cust['customer_type'], cust['Avg_Cart_Value'], color=['#76b7b2','#4e79a7','#f28e2b'], width=0.45)
ax2.set_title('Average Cart Value by Customer Type ($)')
ax2.set_ylabel('Average Cart Value ($)')
for bar, val in zip(bars2, cust['Avg_Cart_Value']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f'${val:.2f}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('reports/customer_type_analysis.png', bbox_inches='tight')
plt.close()
print("6. Customer type chart saved.")

# 7. REVENUE ANALYSIS
order_level = df.drop_duplicates('order_id')
completed_rev = order_level[order_level['abandoned_flag'] == 0]['cart_value'].sum()
lost_rev = order_level[order_level['abandoned_flag'] == 1]['cart_value'].sum()
total_pot_rev = completed_rev + lost_rev

step_rev = (
    order_level[order_level['abandoned_flag'] == 1]
    .groupby('checkout_step')['cart_value']
    .sum()
    .reindex(['Cart', 'Login/Address', 'Shipping', 'Payment'])
    .reset_index()
)
step_rev.columns = ['Step', 'Lost_Revenue']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
ax1.pie([completed_rev, lost_rev], labels=['Captured Revenue', 'Lost to Abandonment'],
        autopct='%1.1f%%', colors=['#59a14f', '#e15759'], startangle=90, explode=(0, 0.08),
        textprops={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title(f'Realized vs Lost Revenue\nTotal Potential: ${total_pot_rev:,.0f}')

bars = ax2.bar(step_rev['Step'], step_rev['Lost_Revenue'], color='#e15759', width=0.5)
ax2.set_title('Revenue Lost by Checkout Drop-off Stage ($)')
ax2.set_ylabel('Revenue Lost ($)')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'${x*1e-6:.1f}M'))
for bar, val in zip(bars, step_rev['Lost_Revenue']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(step_rev['Lost_Revenue'])*0.015,
             f'${val:,.0f}', ha='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/revenue_analysis.png', bbox_inches='tight')
plt.close()
print("7. Revenue chart saved.")
print("All charts successfully generated!")
