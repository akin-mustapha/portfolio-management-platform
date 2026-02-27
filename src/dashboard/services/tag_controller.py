# import os
# from src.shared.database.client import SQLModelClient
# from src.infra.repositories.query_repository import SnapshotSQLQueryRepository
# from dotenv import load_dotenv 

# load_dotenv()


# DATABASE_URL = os.getenv("DATABASE_URL")

# class VendorService:
#     def __init__(self):
#         self.database_client = SQLModelClient(database_url=DATABASE_URL)

#     def get_unrealized_profit(self) -> dict:
#         repo = SnapshotSQLQueryRepository(self.database_client)
#         rows = repo.select_portfolio_unrealized_return()
#         data = [dict(r._mapping) for r in rows]
#         return data