from dotenv import load_dotenv 
import os

from dash import html

from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.infrastructure.repositories.query_repository import SnapshotSQLQueryRepository
from src.dashboard.src.layouts.portfolio import portfolio_layout
from src.dashboard.src.services.portfolio_service import PortfolioService


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

# repo
name = 'asset_snapshot'
repo = SnapshotSQLQueryRepository(database_client)

# extraction
portfolio_profit = PortfolioService(repo).get_unrealized_profit()

# Layout
layout = html.Div(portfolio_layout(portfolio_profit))
