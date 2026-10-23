import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
np.random.seed(42)

print('Step 1: Loading raw data...')
df = pd.read_csv(r'c:\Users\anmol\OneDrive\Desktop\cart project\data\kz.csv')
print(f'  Loaded: {len(df):,} rows')

print('Step 2: Dropping duplicates...')
df = df.drop_duplicates()
print(f'  After dedup: {len(df):,} rows')

print('Step 3: Parsing datetime...')
df['event_time'] = pd.to_datetime(df['event_time'], utc=True)

print('Step 4: Removing corrupt 1970 rows...')
corrupt = (df['event_time'].dt.year == 1970).sum()
df = df[df['event_time'].dt.year != 1970].copy()
print(f'  Removed {corrupt} corrupt rows. Remaining: {len(df):,}')

print('Step 5: Imputing nulls...')
median_price = df['price'].median()
df['user_id']       = df['user_id'].fillna(0).astype('int64')
df['category_code'] = df['category_code'].fillna('Unknown')
df['category_id']   = df['category_id'].fillna(0).astype('int64')
df['brand']         = df['brand'].fillna('Unknown')
df['price']         = df['price'].fillna(median_price)
print(f'  Median price used: {median_price:.2f}')

print('Step 6: Capping price outliers...')
p01 = df['price'].quantile(0.01)
p99 = df['price'].quantile(0.99)
df['price'] = df['price'].clip(lower=p01, upper=p99)
print(f'  Price range after cap: {p01:.2f} to {p99:.2f}')

print('Step 7: Engineering time features...')
df['hour'] = df['event_time'].dt.hour
df['day_of_week'] = df['event_time'].dt.day_name()

def time_bucket(h):
    if 5 <= h < 12:  return 'Morning'
    elif 12 <= h < 17: return 'Afternoon'
    elif 17 <= h < 21: return 'Evening'
    else:              return 'Night'

df['time_bucket'] = df['hour'].apply(time_bucket)
print('  time_bucket done:', dict(df['time_bucket'].value_counts()))

print('Step 8: Cart value per order...')
cart_val = df.groupby('order_id')['price'].sum().rename('cart_value')
df = df.merge(cart_val, on='order_id', how='left')
avg_cv = df['cart_value'].mean()
print(f'  Avg cart value: {avg_cv:.2f}')

print('Step 9: Checkout step...')
ic = df.groupby('order_id')['product_id'].count().rename('interaction_count')
df = df.merge(ic, on='order_id', how='left')

def assign_step(n):
    if   n == 1: return 'Cart'
    elif n == 2: return 'Login/Address'
    elif n == 3: return 'Shipping'
    elif n == 4: return 'Payment'
    else:        return 'Order Confirmation'

df['checkout_step'] = df['interaction_count'].apply(assign_step)
print('  Checkout steps:', dict(df['checkout_step'].value_counts()))

print('Step 10: Simulating device type...')
df['device_type_simulated'] = np.random.choice(
    ['Mobile', 'Desktop', 'Tablet'], size=len(df), p=[0.55, 0.35, 0.10])
print('  Device dist:', dict(df['device_type_simulated'].value_counts()))

print('Step 11: Customer type...')
first_ord = df[df['user_id'] != 0].groupby('user_id')['order_id'].min().rename('first_order_id')
df = df.merge(first_ord, on='user_id', how='left')

def ctype(row):
    if row['user_id'] == 0:
        return 'Anonymous'
    return 'New' if row['order_id'] == row['first_order_id'] else 'Returning'

df['customer_type'] = df.apply(ctype, axis=1)
print('  Customer types:', dict(df['customer_type'].value_counts()))

print('Step 12: Abandoned flag...')
df['abandoned_flag'] = (df['checkout_step'] != 'Order Confirmation').astype(int)
ab_rate = df['abandoned_flag'].mean() * 100
print(f'  Abandonment rate: {ab_rate:.1f}%')

print('Step 13: Saving clean CSV...')
out = r'c:\Users\anmol\OneDrive\Desktop\cart project\data\kz_clean.csv'
df.to_csv(out, index=False)

print()
print('=' * 55)
print('  CLEANING COMPLETE')
print('=' * 55)
print(f'  Final rows    : {len(df):,}')
print(f'  Final columns : {len(df.columns)}')
print(f'  All columns   : {list(df.columns)}')
print(f'  Saved to      : {out}')
print('=' * 55)
