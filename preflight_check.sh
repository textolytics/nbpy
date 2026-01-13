#!/bin/bash
# NBPY Startup Helper - Handles common issues before startup

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Main execution
print_header "NBPY Pre-Startup Health Check"

# Check for conflicting services
echo "Checking for port conflicts..."
if sudo netstat -tulpn 2>/dev/null | grep -q ":8086"; then
    print_warning "Port 8086 is in use"
    INFLUX_PID=$(sudo netstat -tulpn 2>/dev/null | grep ":8086" | awk '{print $NF}' | cut -d'/' -f1 | head -1)
    echo "  Process: $INFLUX_PID"
    
    # Check if it's the system InfluxDB
    if ps aux | grep -q "^root.*influxd.*-config"; then
        print_warning "System InfluxDB service is running"
        echo ""
        echo "Automatically stopping system InfluxDB (required for Docker)..."
        sudo systemctl stop influxdb 2>/dev/null || true
        sleep 2
        echo "Disabling auto-start..."
        sudo systemctl disable influxdb 2>/dev/null || true
        print_success "InfluxDB service stopped and disabled"
    fi
else
    print_success "Port 8086 is available"
fi

echo ""
echo "Checking Docker status..."
if ! sudo docker ps &>/dev/null; then
    print_error "Docker is not accessible"
    echo "Run: sudo usermod -aG docker \$USER"
    exit 1
fi
print_success "Docker is accessible"

echo ""
echo "Checking Docker daemon..."
if ! sudo docker info &>/dev/null; then
    print_warning "Docker daemon not responding, starting..."
    sudo systemctl start docker
    sleep 2
    print_success "Docker daemon started"
else
    print_success "Docker daemon is running"
fi

echo ""
echo "Checking for dangling containers..."
DANGLING=$(sudo docker ps -aq 2>/dev/null | wc -l)
if [ "$DANGLING" -gt 0 ]; then
    print_warning "Found $DANGLING container(s) - cleaning up"
    sudo docker ps -aq 2>/dev/null | xargs -r sudo docker rm -f 2>/dev/null || true
    print_success "Containers cleaned"
else
    print_success "No dangling containers"
fi

echo ""
echo "Checking Python module syntax..."
# Check for syntax errors in publisher files
SYNTAX_ERRORS=0
for file in nbpy/zmq/publishers/*.py; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        :
    else
        print_error "Syntax error in $file"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    print_success "All publisher modules have valid syntax"
else
    print_error "Found $SYNTAX_ERRORS syntax error(s) in publisher modules"
    echo ""
    echo "Common issues:"
    echo "  - 'import *' inside functions/methods (must be at module level)"
    echo "  - Missing parentheses or colons"
    echo "  - Incorrect indentation"
    exit 1
fi

echo ""
echo "Checking InfluxDB retention policy configuration..."
# Verify integration_config.json has proper retention policy structure
if python3 << 'PYEOF'
import json
try:
    with open('integration_config.json', 'r') as f:
        config = json.load(f)
    
    policies = config.get('influxdb', {}).get('retention_policies', {})
    if not policies:
        print("ERROR: No retention policies defined in config")
        exit(1)
    
    for name, policy in policies.items():
        if 'duration' not in policy:
            print(f"ERROR: Retention policy '{name}' missing 'duration'")
            exit(1)
        if 'replication' not in policy:
            print(f"WARNING: Retention policy '{name}' missing 'replication' (will use default)")
    
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
PYEOF
then
    print_success "InfluxDB configuration is valid"
else
    print_error "InfluxDB configuration has issues"
    exit 1
fi

echo ""
print_header "Pre-Startup Check Complete"
echo "System is ready for startup!"
echo ""
echo "Next step:"
echo "  sudo ./startup_guide.sh"
echo ""
