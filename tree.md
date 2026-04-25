# Portfolio Management Platform — Folder Tree

portfolio-management-platform/
│
├── scripts/
│   ├── autobuy/                          # Standalone auto-buy script (APScheduler)
│   │   ├── scheduler.py                  # BlockingScheduler entry point
│   │   ├── strategy.py                   # Buy strategy logic
│   │   ├── budget.py                     # Budget allocation
│   │   ├── t212_client.py                # Trading212 API client
│   │   ├── db.py                         # State persistence
│   │   ├── config.py                     # Config loader
│   │   └── state.json                    # Runtime state
│   └── deploy/                           # Deployment scripts
│
├── frontend/src/                         # React + Vite frontend (:5173)
│   ├── App.tsx
│   ├── main.tsx
│   ├── api/                              # API clients (FastAPI :8001)
│   │   ├── client.ts
│   │   ├── assets.ts
│   │   ├── portfolio.ts
│   │   ├── credentials.ts
│   │   ├── rebalance.ts
│   │   └── tags.ts
│   ├── components/
│   │   ├── atoms/
│   │   │   ├── KpiCard.tsx
│   │   │   ├── MetricInfo.tsx
│   │   │   ├── PnlBadge.tsx
│   │   │   ├── PrivacyValue.tsx
│   │   │   └── TickerLogo.tsx
│   │   ├── charts/
│   │   │   ├── AssetPnlChart.tsx
│   │   │   ├── AssetPriceChart.tsx
│   │   │   ├── AssetReturnChart.tsx
│   │   │   ├── AssetValueChart.tsx
│   │   │   ├── DailyMoversTable.tsx
│   │   │   ├── DrawdownChart.tsx
│   │   │   ├── LosersChart.tsx
│   │   │   ├── OpportunitiesChart.tsx
│   │   │   ├── PortfolioPnlChart.tsx
│   │   │   ├── PortfolioValueChart.tsx
│   │   │   ├── PositionPerformanceMap.tsx
│   │   │   ├── PositionWeightChart.tsx
│   │   │   ├── ProfitabilityChart.tsx
│   │   │   ├── SparklineChart.tsx
│   │   │   ├── UnprofitablePnlChart.tsx
│   │   │   ├── VarByPositionChart.tsx
│   │   │   └── WinnersChart.tsx
│   │   ├── molecules/
│   │   │   ├── FilterBar.tsx
│   │   │   ├── KpiGroup.tsx
│   │   │   ├── KpiRow.tsx
│   │   │   └── Section.tsx
│   │   └── organisms/
│   │       ├── AssetProfileDrawer.tsx
│   │       ├── AssetTable.tsx
│   │       ├── EditTagsModal.tsx
│   │       ├── Navbar.tsx
│   │       ├── RebalanceDrawer.tsx
│   │       ├── SettingsModal.tsx
│   │       └── WorkspaceSplit.tsx
│   ├── pages/portfolio/
│   │   ├── AppShell.tsx
│   │   ├── PortfolioContext.tsx
│   │   └── tabs/
│   │       ├── AssetProfileTab.tsx
│   │       ├── OpportunitiesTab.tsx
│   │       ├── PortfolioTab.tsx
│   │       └── RiskTab.tsx
│   ├── hooks/
│   │   ├── useAssets.ts
│   │   ├── useAssetHistory.ts
│   │   ├── usePortfolio.ts
│   │   └── useRebalance.ts
│   ├── store/
│   │   └── useAppStore.ts
│   ├── constants/
│   │   ├── metricDefinitions.ts
│   │   └── timeframes.ts
│   ├── theme/
│   │   ├── theme.ts
│   │   └── tokens.ts
│   └── utils/
│       └── chartUtils.ts
│
├── src/                                  # Python backend
│   ├── api/                              # FastAPI app (:8001)
│   │   ├── main.py
│   │   ├── serialization.py
│   │   └── routers/
│   │       ├── assets.py
│   │       ├── portfolio.py
│   │       ├── credentials.py
│   │       ├── rebalance.py
│   │       └── tags.py
│   │
│   ├── backend/                          # Domain + services layer
│   │   ├── domain/
│   │   │   ├── portfolio/
│   │   │   │   ├── entities.py
│   │   │   │   ├── interfaces.py
│   │   │   │   └── value_objects.py
│   │   │   └── rebalancing/
│   │   │       ├── entities.py
│   │   │       └── value_objects.py
│   │   ├── application/
│   │   │   ├── portfolio/
│   │   │   │   ├── service.py
│   │   │   │   └── factory.py
│   │   │   └── rebalancing/
│   │   │       ├── service.py
│   │   │       ├── plan_generator.py
│   │   │       └── factory.py
│   │   └── infrastructure/
│   │       ├── credentials/
│   │       │   └── repository.py
│   │       ├── portfolio/
│   │       │   ├── asset_repository.py
│   │       │   ├── asset_tag_repository.py
│   │       │   ├── category_repository.py
│   │       │   ├── industry_repository.py
│   │       │   ├── sector_repository.py
│   │       │   ├── tag_repository.py
│   │       │   └── repository_factory.py
│   │       └── rebalancing/
│   │           ├── rebalance_config_repository.py
│   │           ├── rebalance_plan_repository.py
│   │           └── repository_factory.py
│   │
│   ├── dashboard/                        # Dash app (:8050)
│   │   ├── app.py
│   │   ├── components/atoms/
│   │   │   └── buttons.py
│   │   ├── controllers/
│   │   │   ├── asset_controller.py
│   │   │   ├── asset_profile_controller.py
│   │   │   └── portfolio_controller.py
│   │   ├── infrastructure/repositories/
│   │   │   ├── query_repository.py
│   │   │   └── repository_factory.py
│   │   ├── layouts/
│   │   │   ├── layout.py
│   │   │   ├── sidebar.py
│   │   │   └── horizontal_sidebar.py
│   │   ├── pages/portfolio/
│   │   │   ├── portfolio_page.py
│   │   │   ├── callbacks/
│   │   │   │   ├── data.py
│   │   │   │   ├── filters.py
│   │   │   │   ├── rebalancing.py
│   │   │   │   ├── selection.py
│   │   │   │   ├── settings.py
│   │   │   │   ├── tags.py
│   │   │   │   ├── theme.py
│   │   │   │   ├── ui.py
│   │   │   │   └── _helpers.py
│   │   │   ├── charts/
│   │   │   │   ├── asset_charts.py
│   │   │   │   ├── portfolio_charts.py
│   │   │   │   ├── sparklines.py
│   │   │   │   └── chart_theme.py
│   │   │   ├── components/
│   │   │   │   ├── atoms/
│   │   │   │   │   ├── badges.py
│   │   │   │   │   ├── dropdown.py
│   │   │   │   │   └── formatters.py
│   │   │   │   ├── molecules/
│   │   │   │   │   ├── collapsible_section.py
│   │   │   │   │   └── kpi_card.py
│   │   │   │   └── organisms/
│   │   │   │       ├── asset_table.py
│   │   │   │       ├── filter_bar.py
│   │   │   │       ├── kpi_row.py
│   │   │   │       ├── rebalance_panel.py
│   │   │   │       ├── secondary_kpi.py
│   │   │   │       └── workspace_tabs.py
│   │   │   └── tabs/
│   │   │       ├── tab_portfolio.py
│   │   │       ├── tab_asset_profile.py
│   │   │       ├── tab_opportunities.py
│   │   │       ├── tab_risk.py
│   │   │       └── _helpers.py
│   │   └── presenters/
│   │       ├── asset_presenter.py
│   │       ├── asset_profile_presenter.py
│   │       ├── portfolio_presenter.py
│   │       └── view_models.py
│   │
│   ├── orchestration/prefect/            # Prefect flows
│   │   ├── flow_t212_bronze.py
│   │   ├── flow_t212_silver.py
│   │   ├── flow_t212_gold.py
│   │   ├── flow_t212_history_bronze.py
│   │   ├── flow_fred.py
│   │   ├── flow_rebalance_plan.py
│   │   ├── asset_flow_portfolio.py
│   │   ├── asset_flow_event_producer.py
│   │   └── enrichment_synchronization.py
│   │
│   ├── pipelines/                        # ETL pipeline layer
│   │   ├── application/
│   │   │   ├── protocols.py
│   │   │   ├── policies.py
│   │   │   ├── interfaces/
│   │   │   │   ├── interface_api_client.py
│   │   │   │   └── interface_database_client.py
│   │   │   ├── validators/
│   │   │   │   └── schema_validator.py
│   │   │   └── runners/
│   │   │       ├── pipeline_bronze_t212.py
│   │   │       ├── pipeline_bronze_t212_history.py
│   │   │       ├── pipeline_bronze_fred.py
│   │   │       ├── pipeline_silver_t212.py
│   │   │       ├── pipeline_silver_fred.py
│   │   │       ├── pipeline_gold_t212.py           # canonical gold pipeline
│   │   │       ├── pipeline_asset_portfolio.py
│   │   │       ├── portfolio_enrichment_synchronizer.py
│   │   │       ├── loaders/
│   │   │       │   ├── loader_bronze_t212.py
│   │   │       │   ├── loader_bronze_t212_history.py
│   │   │       │   └── loader_bronze_fred.py
│   │   │       └── events/
│   │   │           ├── trading212_event_producer.py
│   │   │           └── trading212_asset_consumer.py
│   │   ├── domain/
│   │   │   ├── models.py
│   │   │   └── schemas/
│   │   │       ├── bronze/
│   │   │       │   ├── account_api.py
│   │   │       │   ├── asset_api.py
│   │   │       │   └── fred_api.py
│   │   │       ├── silver/
│   │   │       │   ├── account.py
│   │   │       │   ├── asset.py
│   │   │       │   └── fred_observation.py
│   │   │       └── gold/
│   │   │           ├── account_gold.py
│   │   │           └── asset_gold.py
│   │   ├── factories/
│   │   │   ├── pipeline_factory.py
│   │   │   ├── event_producer_factory.py
│   │   │   └── schema.py
│   │   └── infrastructure/
│   │       ├── clients/
│   │       │   ├── api_client_trading212.py
│   │       │   └── api_client_fred.py
│   │       ├── kafka/
│   │       │   ├── producer_origins.py
│   │       │   ├── producer_destination.py
│   │       │   ├── consumer_adapter.py
│   │       │   ├── consumer_db_client.py
│   │       │   ├── consumer_main.py
│   │       │   └── schema/
│   │       │       ├── asset_snapshot.yml
│   │       │       ├── asset_postgres.yml
│   │       │       ├── asset_sqlite.yml
│   │       │       └── dim_asset_postgres.yml
│   │       ├── queries/
│   │       │   ├── bronze/                         # SQL for raw layer
│   │       │   │   ├── t212_snapshot_insert.sql
│   │       │   │   ├── t212_history_insert.sql
│   │       │   │   ├── t212_history_cursor_select.sql
│   │       │   │   ├── t212_history_cursor_upsert.sql
│   │       │   │   ├── fred_observations_insert.sql
│   │       │   │   ├── create_partition.sql
│   │       │   │   ├── v_bronze_account.sql
│   │       │   │   ├── v_bronze_position.sql
│   │       │   │   ├── v_bronze_dividend.sql
│   │       │   │   └── v_bronze_order.sql
│   │       │   ├── silver/                         # SQL for staging layer
│   │       │   │   ├── t212_silver_source.sql
│   │       │   │   ├── fred_silver_source.sql
│   │       │   │   └── fred_observation_start.sql
│   │       │   ├── gold/                           # SQL for analytics layer
│   │       │   │   ├── fact_price.sql
│   │       │   │   ├── fact_valuation.sql
│   │       │   │   ├── fact_return.sql
│   │       │   │   ├── fact_technical.sql
│   │       │   │   ├── fact_signal.sql
│   │       │   │   ├── fact_portfolio_daily.sql
│   │       │   │   ├── dim_asset_seed.sql
│   │       │   │   └── dim_portfolio_seed.sql
│   │       │   └── portfolio/
│   │       │       ├── asset_portfolio_source.sql
│   │       │       ├── asset_portfolio_upsert.sql
│   │       │       ├── sync_asset_tag.sql
│   │       │       ├── sync_category.sql
│   │       │       ├── sync_industry.sql
│   │       │       ├── sync_sector.sql
│   │       │       └── sync_tag.sql
│   │       └── repositories/
│   │           ├── repository_postgres.py
│   │           ├── repository_sqlite.py
│   │           ├── repository_factory.py
│   │           └── dead_letter_destination.py
│   │
│   └── shared/                           # Cross-cutting utilities
│       ├── database/
│       │   ├── client.py
│       │   ├── query_loader.py
│       │   └── queries/
│       │       ├── create_mock.sql
│       │       └── most_recent_asset.sql
│       ├── notifications/
│       │   └── email.py
│       ├── repositories/
│       │   ├── base_table_repository.py
│       │   └── interface.py
│       └── utils/
│           └── custom_logger.py
