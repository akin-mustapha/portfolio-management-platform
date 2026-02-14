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
# ==============================
# asset ingestion flow
echo -e "${GREEN}Starting Bronze Asset Pipeline...${NC}"
python3 -m orc.prefect.bronze_asset_flow > logs/bronze_asset_flow.log 2>&1 & BRONZE_ASSET_FLOW_PID=$!

echo -e "${GREEN}Starting Silver Asset Pipeline...${NC}"
python3 -m src.prefect.silver_asset_pipeline_flow > logs/silver_asset_pipeline_flow.log 2>&1 & SILVER_ASSET_FLOW_PID=$!

echo -e "${GREEN}Starting Silver Asset Compute Pipeline...${NC}"
python3 -m orc.prefect.silver_asset_compute_flow > logs/silver_asset_compute_flow.log 2>&1 & SILVER_ASSET_COMPUTED_FLOW_PID=$!

echo -e "${GREEN}Starting Portfolio Asset Pipeline...${NC}"
python3 -m src.orc.prefect.portfolio_asset_flow > logs/portfolio_asset_flow_run.log 2>&1 & PORTFOLIO_ASSET_FLOW_PID=$!

# echo -e "${GREEN}Starting the Asset Ingestion Event Producer${NC}"
# python3 -m orc.prefect.asset_flow_event_producer > logs/asset_flow_event_producer.log 2>&1 & asset_flow_event_producer_PID=$!



echo -e "${GREEN} Running...${NC}"
echo "Server PID: $SERVER_PID"
echo "Agent PID: $AGENT_PID"

echo "Bronze Asset Flow PID: $BRONZE_ASSET_FLOW_PID"
echo "Silver Asset Flow PID: $SILVER_ASSET_FLOW_PID"
echo "Silver Asset Computed Flow PID: $SILVER_ASSET_COMPUTED_FLOW_PID"
# echo "Asset_flow_event_producer PID: $asset_flow_event_producer_PID"

trap "echo -e '${GREEN}Stopping all processes...${NC}'; kill $SERVER_PID $AGENT_PID $FLOW_PID; exit" SIGINT SIGTERM

wait