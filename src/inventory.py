
def daily_sales(df):
    df_copy = df.copy()

    daily_product_sales = (
        df_copy
        .groupby(['product', 'date'])['quantity']
        .sum()
        .reset_index()
    )

    daily_sales = (
        daily_product_sales
        .groupby('priduct')['quantity']
        .mean()
        .reset_index()
        .rename(columns={'quantity':'avg_daily_sales'})
    )
    return daily_sales

def inventory_level(df):
    df_copy = df.copy()

    current_level = (
        df_copy
        .groupby('product')['inventory']
        .last()
        .reset_index()
    )
    return current_level

def stock_status(days):
    if days < 7:
        return "Critical"
    elif days < 30:
        return "Reorder Soon"
    else:
        return "Healthy"