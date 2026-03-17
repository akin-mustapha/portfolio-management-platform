#!/bin/bash
set -e

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}Changing directory to src...${NC}"
cd src

mkdir -p logs

echo -e "${GREEN}Starting Prefect Orion server...${NC}"
prefect server start > logs/prefect_server.log 2>&1 & SERVER_PID=$!

sleep 5

# prefect worker start --pool "my-docker-pool"
# sleep 5


echo -e "${GREEN}Starting Prefect agent...${NC}"
prefect agent start -q default > logs/prefect_agent.log 2>&1 & AGENT_PID=$!

sleep 5

# =====================================
# flows
# ==============================
# asset ingestion flow
echo -e "${GREEN}Starting Asset Pipeline Bronze...${NC}"
python3 -m orchestration.prefect.asset_flow_bronze > logs/asset_flow_bronze.log 2>&1 & ASSET_FLOW_BRONZE_PID=$!

echo -e "${GREEN}Starting Asset Pipeline Silver...${NC}"
python3 -m orchestration.prefect.asset_flow_silver > logs/asset_flow_silver.log 2>&1 & ASSET_FLOW_SILVER_PID=$!

echo -e "${GREEN}Starting Portfolio Asset Pipeline...${NC}"
python3 -m orchestration.prefect.asset_flow_portfolio > logs/asset_flow_portfolio.log 2>&1 & ASSET_FLOW_PORTFOLIO_PID=$!


# Account ingetion
echo -e "${GREEN}Starting Account Pipeline Bronze...${NC}"
python3 -m orchestration.prefect.account_flow_bronze > logs/account_flow_bronze.log 2>&1 & ACCOUNT_FLOW_BRONZE_PID=$!

echo -e "${GREEN}Starting Account Pipeline Silver...${NC}"
python3 -m orchestration.prefect.account_flow_silver > logs/account_flow_silver.log 2>&1 & ACCOUNT_FLOW_SILVER_PID=$!

echo -e "${GREEN}Starting Enrichment Sync...${NC}"
python3 -m orchestration.prefect.enrichment_synchronization > logs/enrichment_sync.log 2>&1 & ENRICHMENT_SYNC_PID=$!

# echo -e "${GREEN}Starting the Asset Ingestion Event Producer${NC}"
# python3 -m orchestration.prefect.asset_flow_event_producer > logs/asset_flow_event_producer.log 2>&1 & asset_flow_event_producer_PID=$!



echo -e "${GREEN}Running...${NC}"
echo "Server PID: $SERVER_PID"
echo "Agent PID: $AGENT_PID"

echo "Asset Flow Bronze PID: $ASSET_FLOW_BRONZE_PID"
echo "Asset Flow Silver PID: $ASSET_FLOW_SILVER_PID"
echo "Asset Flow Portfolio PID: $ASSET_FLOW_PORTFOLIO_PID"
echo "Account Flow Bronze PID: $ACCOUNT_FLOW_BRONZE_PID"
echo "Account Flow Silver PID: $ACCOUNT_FLOW_SILVER_PID"
echo "Enrichment Sync PID: $ENRICHMENT_SYNC_PID"
# echo "Asset_flow_event_producer PID: $asset_flow_event_producer_PID"

trap "echo -e '${GREEN}Stopping all processes...${NC}'; kill $SERVER_PID $AGENT_PID $FLOW_PID; exit" SIGINT SIGTERM

wait