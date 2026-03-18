from fastapi import FastAPI
from fastapi.security import HTTPBearer
from src.data_loader import load_csv
from src.cleaning import cleaning
from src.kpis import calculate_revenue_profit, calculate_growth, calculate_cac, calculate_traffic, calculate_best_seller
from helpers import INCLUDE_NEGATIVE_AMOUNTS, TIME_GRAIN
from src.forecasting import forecast

app = FastAPI(
    title="Sales Dashboard",
    version="1.0.0"
)

bearer_scheme = HTTPBearer()

app.openapi_schema = None

if __name__ == "__main__":
    df = load_csv("/home/lidia/sales_dashboard/data/raw/online_retail_II.csv")
    df = cleaning(df)

    # df_rev = calculate_revenue_profit(df)
    # df_gr = calculate_growth(df)
    # df_bs = calculate_best_seller(df)
    # print(f"Revenue : {df_rev}")
    # print(f"Growth : {df_gr}")
    # print(f"Best Seller : {df_bs}")
    m_rev = forecast(df)
