#!/bin/bash
set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

mkdir -p logs

echo -e "${GREEN}Starting Prefect server...${NC}"
prefect server start > logs/prefect_server.log 2>&1 & SERVER_PID=$!

sleep 5

echo -e "${GREEN}Creating work pool (skips if already exists)...${NC}"
prefect work-pool create asset-monitoring-pool --type process 2>/dev/null || echo "Work pool already exists"

echo -e "${GREEN}Deploying all flows from prefect.yaml...${NC}"
prefect deploy --all

echo -e "${GREEN}Starting worker...${NC}"
prefect worker start --pool asset-monitoring-pool > logs/prefect_worker.log 2>&1 & WORKER_PID=$!

echo -e "${GREEN}Running...${NC}"
echo "Server PID: $SERVER_PID"
echo "Worker PID: $WORKER_PID"

trap "echo -e '${GREEN}Stopping all processes...${NC}'; kill $SERVER_PID $WORKER_PID; exit" SIGINT SIGTERM

wait
