import pandas as pd

class PortfolioService:
    def __init__(self, repo):
        self.repo = repo
    def get_unrealized_profit(self):
        rows = self.repo.select_portfolio_unrealized_return()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
        return df