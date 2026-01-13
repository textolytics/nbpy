#!/bin/bash
# NBPY Integrated Startup - Step-by-Step Guide

# This script provides a guided walkthrough of starting the NBPY system

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}STEP $1${NC}: $2"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_section() {
    echo -e "\n${BLUE}──────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${BLUE}──────────────────────────────────────────────────────────${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

read_continue() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Main guide
clear

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     NBPY INTEGRATED ZMQ MICROSERVICES STARTUP GUIDE      ║
║                                                           ║
║     Complete integration of:                            ║
║     - Docker containers (InfluxDB + Grafana)           ║
║     - ZMQ publishers (5 data sources)                  ║
║     - ZMQ subscribers (3 data sinks)                   ║
║     - InfluxDB (time-series persistence)              ║
║     - Grafana (real-time dashboards)                  ║
║     - Message validation & health monitoring          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

read_continue

# Step 1: Verify Requirements
print_step 1 "Verify System Requirements"

print_section "Checking installed tools..."

if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    print_success "Docker installed: $docker_version"
else
    print_error "Docker not installed"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    print_success "docker-compose installed: $compose_version"
else
    print_error "docker-compose not installed"
    echo "Install docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    print_success "Python3 installed: $python_version"
else
    print_error "Python3 not installed"
    exit 1
fi

read_continue

# Step 2: Check Virtual Environment
print_step 2 "Check Python Virtual Environment"

print_section "Verifying Python virtual environment..."

if [ -f "${SCRIPT_DIR}/nbpy/bin/python" ]; then
    print_success "Virtual environment found: ${SCRIPT_DIR}/nbpy"
else
    print_warning "Virtual environment not found, creating..."
    python3 -m venv "${SCRIPT_DIR}/nbpy"
    print_success "Virtual environment created"
fi

print_section "Installing Python packages..."

"${SCRIPT_DIR}/nbpy/bin/pip" install -q --upgrade pip 2>/dev/null || true
"${SCRIPT_DIR}/nbpy/bin/pip" install -q msgpack influxdb pyzmq requests 2>/dev/null || true

print_success "Python packages installed"
read_continue

# Step 3: Check Configuration
print_step 3 "Verify Configuration"

print_section "Checking configuration files..."

if [ -f "${SCRIPT_DIR}/integration_config.json" ]; then
    print_success "integration_config.json found"
else
    print_error "integration_config.json not found"
    exit 1
fi

if [ -f "${SCRIPT_DIR}/docker-compose.yml" ]; then
    print_success "docker-compose.yml found"
else
    print_error "docker-compose.yml not found"
    exit 1
fi

if [ -f "${SCRIPT_DIR}/integrated_startup.sh" ]; then
    print_success "integrated_startup.sh found"
else
    print_error "integrated_startup.sh not found"
    exit 1
fi

print_section "Configuration summary:"
echo "  Config file:     ${SCRIPT_DIR}/integration_config.json"
echo "  Docker compose:  ${SCRIPT_DIR}/docker-compose.yml"
echo "  Startup script:  ${SCRIPT_DIR}/integrated_startup.sh"
echo "  Log directory:   ${SCRIPT_DIR}/logs"

read_continue

# Step 4: Check Ports
print_step 4 "Check Port Availability"

print_section "Checking required ports..."

check_port() {
    local port=$1
    local name=$2
    
    if nc -z localhost "${port}" 2>/dev/null; then
        print_warning "Port ${port} (${name}) is in use"
        return 1
    else
        print_success "Port ${port} (${name}) is available"
        return 0
    fi
}

all_available=true

check_port 8086 "InfluxDB" || all_available=false
check_port 3000 "Grafana" || all_available=false
check_port 5558 "Kraken Tick" || all_available=false
check_port 5560 "Kraken Depth" || all_available=false

if [ "$all_available" = false ]; then
    print_warning "Some ports are in use. Please stop other services or modify ports."
    echo "To find what's using a port: sudo lsof -i :<PORT>"
fi

read_continue

# Step 5: Review Architecture
print_step 5 "Review System Architecture"

print_section "Data flow:"

cat << "EOF"
Publishers (Kraken, OANDA, Betfair)
    ↓
    ZMQ Topics (tcp://localhost:555x)
    ↓
Subscribers (Listen and forward)
    ↓
    InfluxDB (Persist with retention policies)
    ↓
    Grafana (Visualize in dashboards)
EOF

echo ""
print_section "Startup sequence:"

echo "  Phase 1: Docker Containers         (15 seconds)"
echo "    • Start InfluxDB container"
echo "    • Start Grafana container"
echo "    • Verify health endpoints"
echo ""
echo "  Phase 2: InfluxDB Setup           (5 seconds)"
echo "    • Create 'tick' database"
echo "    • Configure retention policies (7d, 30d, 365d)"
echo "    • Create measurement schemas"
echo ""
echo "  Phase 3: ZMQ Publishers           (3 seconds)"
echo "    • Start Kraken tick publisher"
echo "    • Start Kraken depth publisher"
echo "    • Start OANDA tick publisher"
echo "    • Start Betfair stream publisher"
echo ""
echo "  Phase 4: Grafana Dashboards       (5 seconds)"
echo "    • Create InfluxDB datasource"
echo "    • Auto-provision 5 dashboards"
echo ""
echo "  Phase 5: Message Validation       (15 seconds)"
echo "    • Monitor ZMQ topics for messages"
echo "    • Verify InfluxDB data ingestion"
echo "    • Validate complete pipeline"
echo ""

print_section "Total estimated startup time: 45-60 seconds"

read_continue

# Step 6: Ready to Start
print_step 6 "Ready to Start System"

print_section "Summary of what will happen:"

echo "✓ All Docker containers will be started"
echo "✓ All ZMQ services will be launched"
echo "✓ All data will be persisted to InfluxDB"
echo "✓ All dashboards will be created in Grafana"
echo "✓ Complete message validation will be performed"
echo "✓ System health will be verified"
echo ""

print_section "After startup, you can access:"

echo "  Grafana:        http://localhost:3000"
echo "                  Username: admin"
echo "                  Password: admin123"
echo ""
echo "  InfluxDB API:   http://localhost:8086"
echo "                  Username: zmq"
echo "                  Password: zmq"
echo ""
echo "  Logs:           ${SCRIPT_DIR}/logs/"
echo "                  Main log: integrated_startup.log"
echo ""

# Step 7: Start the System
print_step 7 "Start the System"

echo -e "${YELLOW}Do you want to start the system now? (yes/no)${NC}"
read -r response

if [ "$response" != "yes" ]; then
    echo "Startup cancelled. You can start manually with:"
    echo ""
    echo "  ${SCRIPT_DIR}/integrated_startup.sh start"
    echo ""
    exit 0
fi

clear

echo -e "${GREEN}Starting NBPY Integrated System...${NC}\n"

cd "${SCRIPT_DIR}"
./integrated_startup.sh start

exit_code=$?

# Step 8: Post-Startup
print_step 8 "Post-Startup Verification"

if [ $exit_code -eq 0 ]; then
    print_success "System started successfully!"
    
    print_section "Next steps:"
    
    echo "1. Open Grafana in your browser:"
    echo "   http://localhost:3000"
    echo ""
    echo "2. View your dashboards:"
    echo "   - Kraken Tick Stream"
    echo "   - Kraken Depth Stream"
    echo "   - OANDA Tick Stream"
    echo "   - Betfair Stream"
    echo ""
    echo "3. Monitor system health:"
    echo "   python3 db/health_check.py monitor"
    echo ""
    echo "4. View logs:"
    echo "   tail -f logs/integrated_startup.log"
    echo ""
    echo "5. Stop the system when done:"
    echo "   ./integrated_startup.sh stop"
    echo ""
else
    print_error "System startup failed!"
    
    print_section "Troubleshooting:"
    
    echo "1. Check startup logs:"
    echo "   tail -f logs/integrated_startup.log"
    echo ""
    echo "2. Check Docker logs:"
    echo "   docker-compose logs"
    echo ""
    echo "3. Check service logs:"
    echo "   ls -la logs/"
    echo ""
    echo "4. For detailed help, see:"
    echo "   cat INTEGRATION_STARTUP.md"
    echo ""
    
    exit 1
fi

print_section "System is now running!"

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ STARTUP GUIDE COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}\n"
