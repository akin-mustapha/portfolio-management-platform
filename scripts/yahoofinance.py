import yfinance as yf
from sqlmodel import Session, create_engine, text, SQLModel
import pandas as pd

if __name__ == "__main__":

  database_url = 'sqlite:///./data/database/dev_1.db'

  db_client = create_engine(database_url, echo=True)

  SQLModel.metadata.create_all(db_client)
  query = """SELECT *
    FROM asset
  """
  with Session(db_client) as s:
    res = s.exec(text(query))
    s.commit()
  columns = list(res.keys())
  rows = res.all()

  asset_df = pd.DataFrame(data=rows, columns=columns)

  breakpoint()
  # for row in res:
  #   print(row)


  # apple= yf.Ticker("aapl")

  # # show actions (dividends, splits)
  # apple.actions

  # # show dividends
  # apple.dividends

  # # show splits
  # apple.splits

  # print(apple.actions)

  # + other methods etc.