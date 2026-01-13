#!/bin/bash

# Docker Restart Script for nbpy InfluxDB & Grafana
# Handles port conflicts and graceful cleanup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="nbpy"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Docker Services Restart - nbpy Project                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running with sudo (required for docker)
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run with sudo for Docker operations"
    exec sudo "$0" "$@"
fi

# Step 1: Stop and remove existing containers
echo ""
echo "📋 Step 1: Cleaning up existing containers..."

if docker ps -a 2>/dev/null | grep -q "${PROJECT_NAME}_influxdb"; then
    print_warning "Found existing InfluxDB container"
    docker stop ${PROJECT_NAME}_influxdb 2>/dev/null || true
    sleep 2
    docker rm ${PROJECT_NAME}_influxdb 2>/dev/null || true
    print_status "InfluxDB container removed"
fi

if docker ps -a 2>/dev/null | grep -q "${PROJECT_NAME}_grafana"; then
    print_warning "Found existing Grafana container"
    docker stop ${PROJECT_NAME}_grafana 2>/dev/null || true
    sleep 2
    docker rm ${PROJECT_NAME}_grafana 2>/dev/null || true
    print_status "Grafana container removed"
fi

# Step 2: Stop system InfluxDB service if running
echo ""
echo "📋 Step 2: Stopping system services..."

systemctl stop influxdb 2>/dev/null || service influxdb stop 2>/dev/null || true
sleep 2
print_status "System services stopped"

# Step 2b: Kill any remaining processes using the ports
echo ""
echo "📋 Step 2b: Clearing ports 8086 and 3000..."

for port in 8086 3000; do
    PID=$(ss -tlnp 2>/dev/null | grep ":$port " | awk '{print $NF}' | grep -oP '\d+' | head -1)
    if [[ ! -z "$PID" ]]; then
        print_warning "Process (PID: $PID) found on port $port, killing..."
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
    
    # Double-check the port is free
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        print_error "Port $port still in use!"
    else
        print_status "Port $port cleared"
    fi
done

# Step 3: Remove dangling networks/volumes if requested
echo ""
echo "📋 Step 3: Cleaning up Docker resources..."

docker network prune -f 2>/dev/null || true
print_status "Removed unused networks"

# Step 4: Verify docker-compose.yml exists
echo ""
echo "📋 Step 4: Verifying configuration..."

if [[ ! -f "$SCRIPT_DIR/docker-compose.yml" ]]; then
    print_error "docker-compose.yml not found in $SCRIPT_DIR"
    exit 1
fi
print_status "docker-compose.yml found"

# Step 5: Start services with docker-compose
echo ""
echo "📋 Step 5: Starting services..."
echo ""

cd "$SCRIPT_DIR"

docker-compose up -d

if [[ $? -eq 0 ]]; then
    print_status "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 6: Wait for services to be healthy
echo ""
echo "📋 Step 6: Waiting for services to be ready..."
echo ""

MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker-compose ps 2>/dev/null | grep -q "influxdb.*Up"; then
        print_status "InfluxDB is running"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 1
done

echo ""

# Step 7: Verify services
echo ""
echo "📋 Step 7: Verifying services..."
echo ""

docker-compose ps

echo ""
echo "📋 Step 8: Testing connectivity..."
echo ""

if curl -s -u zmq:zmq http://localhost:8086/ping > /dev/null 2>&1; then
    print_status "InfluxDB is responding"
else
    print_warning "InfluxDB not responding yet (may need more time)"
fi

# Final status
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Restart Complete!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Services running at:"
echo "  • InfluxDB:  http://localhost:8086"
echo "  • Grafana:   http://localhost:3000 (admin/admin)"
echo ""
echo "Useful commands:"
echo "  docker-compose ps              - Show service status"
echo "  docker-compose logs -f         - Follow logs"
echo "  docker-compose logs -f influxdb - InfluxDB logs only"
echo "  docker-compose down            - Stop services"
echo ""
print_status "All done!"
