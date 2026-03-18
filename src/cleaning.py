import pandas as pd

# required_fields = {"order", "customer", "product", "date", "traffic_source", "marketing_spend"}
required_fields = {}

def cleaning(df):
    for col in required_fields:
        if col in df.columns:
            print("The required column is present")
        else:
            raise Exception("One or more required columns are missing")


    df['revenue'] = df['quantity'] * df['unit_price']  
    df['date'] = pd.to_datetime(df['date'])  

    missing_values = len(df) - len(df.dropna())
    print(f"The number of rows with missing values to be dropped : {missing_values}")

    duplicates = df.duplicated().sum()
    df.drop_duplicates(inplace=True)
    print(f"The number of rows duplicated to be dropped : {duplicates}")


    return df