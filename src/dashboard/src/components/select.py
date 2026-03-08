import dash_bootstrap_components as dbc

def create_select(df, select_id="asset-select", label="asset_name", value="asset_id"):
    return dbc.Select(
        id=select_id,
        options=[
            {
                "label": row[label],
                "value": row[value],
            }
            for _, row in df.iterrows()
        ],
        placeholder="Select asset",
    )