import pandas as pd

def load_dataframe(csv_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    """

    df = pd.read_csv(csv_path)

    return df


def summarize_dataframe(df: pd.DataFrame) -> dict:
    """
    Generate metadata about the dataframe.
    """

    summary = {
        "shape": {
            "rows": df.shape[0],
            "columns": df.shape[1]
        },

        "columns": {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        },

        "sample_values": {
            col: df[col]
                    .dropna()
                    .astype(str)
                    .head(3)
                    .tolist()

            for col in df.columns
        },

        "missing_values": {
            col: int(count)
            for col, count in df.isnull().sum().items()
        }
    }

    return summary