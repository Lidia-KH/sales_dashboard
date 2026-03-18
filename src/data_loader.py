import pandas as pd

def load_csv(path):
    df = pd.read_csv(path, sep=None, engine="python")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    print(df.shape)
    print(df.columns)
    print(df)
    return df