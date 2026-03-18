import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

def forecast(df, horizon=3):
    df_copy = df.copy()
    monthly_revenue = (
        df_copy
        .set_index('date')
        .resample('ME')['revenue']
        .sum()
        .reset_index()
    )
    months = monthly_revenue['date'].dt.month
    monthly_revenue['months'] = months
    monthly_revenue['t'] = months.index

    last_t = monthly_revenue['t'].iloc[-1]
    future_t = np.arange(last_t + 1, last_t + horizon + 1)

    last_date = monthly_revenue['date'].iloc[-1]
    future_dates = pd.date_range(
        start= last_date + pd.offsets.MonthEnd(1),
        periods=horizon,
        freq='ME'
    )

    future_months = future_dates.month

    encoder = OneHotEncoder(sparse_output=False)
    encoded_data = encoder.fit_transform(monthly_revenue[['months']])
    encoded = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(['months']))

    future_encoded = encoder.transform(future_months.to_frame(name='months'))

    X = np.hstack((
        monthly_revenue[['t']],
        encoded
    ))

    future_X = np.hstack((
        future_t.reshape(-1, 1),
        future_encoded
    ))

    y = monthly_revenue['revenue']

    split = int(len(X) * 0.8)

    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    poly = PolynomialFeatures(degree=1, include_bias=False)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)
    future_X_poly = poly.transform(future_X)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)
    # model.fit(X_train, y_train)

    y_pred = model.predict(X_test_poly)
    future_pred = model.predict(future_X_poly)

    future_df = pd.DataFrame({
        'date': future_dates,
        'forecast_revenue': future_pred
    })

    history_df = monthly_revenue[['date', 'revenue']]
    history_df = history_df.rename(columns={'revenue':'actual_revenue'})

    future_df['actual_revenue'] = np.nan
    history_df['forecast_revenue'] = np.nan

    forecast_df = pd.concat([future_df, history_df])
    # y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    return forecast_df
    # print(monthly_revenue)

    # print(f'R square Score: {r2:.04f}')
    # print(f'Mean square Error: {mse:.04f}')
