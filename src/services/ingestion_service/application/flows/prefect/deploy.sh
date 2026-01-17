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
echo -e "${GREEN}Starting the asset ingestion...${NC}"
python3 -m prefect_flow.ingestion_flow.asset_flow > logs/asset_flow_run.log 2>&1 & ASSET_FLOW_PID=$!

echo -e "${GREEN}Starting the asset snapshot ingestion...${NC}"
python3 -m prefect_flow.ingestion_flow.asset_snapshot_flow > logs/asset_snapshot_flow_run.log 2>&1 & ASSET_SNAPSHOT_FLOW_PID=$!

echo -e "${GREEN}Starting the portfolio snapshot flow...${NC}"
python3 -m prefect_flow.ingestion_flow.portfolio_snapshot_flow > logs/portfolio_snapshot_flow_run.log 2>&1 & PORTFOLIO_SNAPSHOT_FLOW_PID=$!


echo -e "${GREEN} Running flow...${NC}"
echo "Server PID: $SERVER_PID"
echo "Agent PID: $AGENT_PID"
echo "Flow PID: $ASSET_FLOW_PID"
echo "Flow PID: $ASSET_SNAPSHOT_FLOW_PID"
echo "Flow PID: $PORTFOLIO_SNAPSHOT_FLOW_PID"


trap "echo -e '${GREEN}Stopping all processes...${NC}'; kill $SERVER_PID $AGENT_PID $FLOW_PID; exit" SIGINT SIGTERM

wait