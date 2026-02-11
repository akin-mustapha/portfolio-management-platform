#!/bin/bash
set -e

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

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
# =====================================
# TODO: Convert into a loop, reads all flow from flow folder and automatically deploys them.

# asset ingestion flow

echo -e "${GREEN}Starting the Asset ingestion...${NC}"
python3 -m orc.prefect.asset_flow > logs/asset_flow_run.log 2>&1 & ASSET_FLOW_PID=$!

# echo -e "${GREEN}Starting the Asset snapshot ingestion...${NC}"
# python3 -m src.prefect.asset_snapshot_flow > logs/asset_snapshot_flow_run.log 2>&1 & ASSET_SNAPSHOT_FLOW_PID=$!

echo -e "${GREEN}Starting the Portfolio snapshot flow...${NC}"
python3 -m src.orc.prefect.portfolio_snapshot_flow > logs/portfolio_snapshot_flow_run.log 2>&1 & PORTFOLIO_SNAPSHOT_FLOW_PID=$!

echo -e "${GREEN}Starting the Asset metric flow...${NC}"
python3 -m orc.prefect.asset_metric_flow > logs/asset_metric_flow.log 2>&1 & ASSET_METRIC_FLOW_PID=$!

echo -e "${GREEN}Starting the Asset Ingestion Event Producer${NC}"
python3 -m orc.prefect.asset_flow_event_producer > logs/asset_flow_event_producer.log 2>&1 & asset_flow_event_producer_PID=$!



echo -e "${GREEN}Starting the Asset Ingestion Event Producer${NC}"
python3 -m orc.prefect.asset_full_loader_flow > logs/asset_full_loader_flow.log 2>&1 & ASSET_FULL_LOADER_FLOW_PID=$!

echo -e "${GREEN}Starting the Asset Silver Batch Job${NC}"
python3 -m orc.prefect.silver_asset_pipeline_flow > logs/silver_asset_pipeline_flow.log 2>&1 & SILVER_ASSET_PIPELINE_FLOW_PID=$!


echo -e "${GREEN} Running flow...${NC}"
echo "Server PID: $SERVER_PID"
echo "Agent PID: $AGENT_PID"
echo "Asset_flow PID: $ASSET_FLOW_PID"
# echo "Asset_snapshot_flow PID: $ASSET_SNAPSHOT_FLOW_PID"
echo "Portfolio_snapshot_flow PID: $PORTFOLIO_SNAPSHOT_FLOW_PID"
echo "Asset_metric_flow PID: $ASSET_METRIC_FLOW_PID"
echo "Asset_flow_event_producer PID: $asset_flow_event_producer_PID"
echo "Asset_full_loader_flow PID: $ASSET_FULL_LOADER_FLOW_PID"
echo "Silver_asset_pipeline_flow PID: $SILVER_ASSET_PIPELINE_FLOW_PID"

trap "echo -e '${GREEN}Stopping all processes...${NC}'; kill $SERVER_PID $AGENT_PID $FLOW_PID; exit" SIGINT SIGTERM

wait