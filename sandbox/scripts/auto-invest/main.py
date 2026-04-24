"""

This script is responsible for executing the auto-investment strategy based on the configuration defined in `config.yaml`. It reads the configuration, calculates the target allocations, and executes trades accordingly.


python ./sandbox/scripts/auto-invest/main.py
"""
from unittest import result

from prefect import logging
from sqlmodel import SQLModel, Session, create_engine, text
import yaml
import requests



def load_config():
    import os
    from dotenv import load_dotenv

    load_dotenv()
    config = yaml.load(open("sandbox/scripts/auto-invest/config.yaml"), Loader=yaml.FullLoader)
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "BUDGET": float(config.get("budget", 0)),
        "ASSETS": [
            {
                "name": asset.get("name"),
                "ticker": asset.get("ticker"),
                "allocation": float(asset.get("allocation"))
            }
            for asset in config.get("assets", [])
        ]
    }
    
    


class SQLModelClient:
    """SQLModel client for database operations."""
    def __init__(self, database_url: str, echo: bool = False):
        super().__init__()
        self.engine = create_engine(database_url, echo=echo)
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def close(self) -> None:
        if self.session:
            self.session.close()

    def execute(self, query: str, params=None):
        if not self.session:
            raise RuntimeError("Database session is not established.")
        result = None
        try:
            with self.session as s:
                result = s.exec(text(query), params=params or {})
                s.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
        return result


def create_order(ticker: str, quantity: int):
    """
    Placeholder function to create an order. In a real implementation, this would interact with a brokerage API.
    """
    url = "https://demo.trading212.com/api/v0/equity/orders/market"

    payload = {
      "extendedHours": True,
      "quantity": quantity,
      "ticker": ticker
    }

    headers = {
      "Content-Type": "application/json",
      "Authorization": "YOUR_API_KEY_HERE"
    }

    # response = requests.post(url, json=payload, headers=headers, auth=('<username>','<password>'))

    # data = response.json()
    print(f"API Request to create order: {payload}")
    print(f"Creating order for {quantity} shares of {ticker}")
    

def main():
    config = load_config()
    print("Loaded configuration:", config)

    # Calculate target allocations and create orders
    for asset in config["ASSETS"]:
        target_value = config["BUDGET"] * asset["allocation"]
        print(f"Target value for {asset['ticker']}: ${target_value:.2f}")
        
        # Placeholder: Assume we get the current price from somewhere
        
        sql = """
        SELECT price
          FROM analytics.fact_price t1
            INNER JOIN analytics.dim_asset t2 ON t1.asset_id = t2.asset_id
          WHERE t2.ticker = :ticker
          ORDER BY t1.created_timestamp
          DESC LIMIT 1"""
          
        client = SQLModelClient(config["DATABASE_URL"])
        result = client.execute(sql, params={"ticker": asset["ticker"]}).fetchone()
        current_price = float(result.price) if result else 0.0
        
        client.close()
        quantity = float(target_value / current_price)
        
        create_order(asset["ticker"], quantity)
        
        
if __name__ == "__main__":
    main()