# KPI calculations: revenue, profit, CAC, growth, best seller, traffic breakdown

import numpy as np


def calculate_revenue_profit(df, TIME_GRAIN, INCLUDE_NEGATIVE_AMOUNTS):
    df_copy = df.copy()

    if not INCLUDE_NEGATIVE_AMOUNTS:
        df_copy = df_copy[df_copy['quantity']>=0]

    if 'unit_cost' is df_copy.columns:
        df_copy['profit'] = df_copy['revenue'] - (df_copy['quantity'] * df_copy['unit_price'])
    else:
        df_copy['profit'] = np.nan

    df_revenue_profit = (
        df_copy
        .set_index('date')
        .resample(TIME_GRAIN)[['revenue', 'profit']]
        .sum()
        .reset_index()
    )

    return df_revenue_profit

def calculate_growth(df):
    df_copy = df.copy()

    df_growth = (
        df_copy
        .set_index('date')
        .resample('ME')['revenue']
        .sum()
        .pct_change() 
        .reset_index()
    )
    df_growth.columns = ['date', 'growth_pct']
    df_growth['growth_pct'] = df_growth['growth_pct'] * 100

    return df_growth

def calculate_best_seller(df):
    df_copy = df.copy().reset_index(drop=True)

    df_best_seller_quantity = (
        df_copy
        .groupby('product')['quantity']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    df_best_seller_revenue = (
        df_copy
        .groupby('product')['revenue']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return df_best_seller_quantity, df_best_seller_revenue

def calculate_traffic(df):
    df_copy = df.copy()

    if 'traffic_source' in df_copy.columns:
        df_traffic = (
            df_copy['traffic_source']
            .value_counts(normalize=True) 
            .reset_index()

        )
        df_traffic.columns = ['traffic_source', 'percentage']
        df_traffic['percentage'] = df_traffic['percentage'] * 100
    else:
        df_traffic = np.nan

    return df_traffic

def calculate_cac(df):
    monthly = df.groupby(df['date'].dt.to_period("M")).agg(
        spend = ('marketing_spend', 'first'),
        new_customers = ('customer_id', 'nunique')
    )

    monthly['cac'] = monthly['spend'] / monthly['new_customers']

    return monthly.reset_index()


