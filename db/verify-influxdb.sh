#!/bin/bash

# InfluxDB Container Verification Script
# Tests all InfluxDB endpoints on port 8086

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        InfluxDB Container - Port 8086 Verification            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
}

# Test 1: Health/Ping
echo "📋 Test 1: InfluxDB Ping (Health Check)"
if curl -s -u zmq:zmq http://localhost:8086/ping > /dev/null 2>&1; then
    print_pass "InfluxDB is running and responding to health checks"
else
    print_fail "InfluxDB health check failed"
    exit 1
fi

# Test 2: HTTP API Version
echo ""
echo "📋 Test 2: InfluxDB HTTP API Version"
VERSION=$(curl -s -u zmq:zmq http://localhost:8086/ping -I 2>/dev/null | grep -i "x-influxdb-version" | cut -d' ' -f2 | tr -d '\r')
if [[ ! -z "$VERSION" ]]; then
    print_pass "InfluxDB version: $VERSION"
else
    print_fail "Could not retrieve version"
fi

# Test 3: Database Check
echo ""
echo "📋 Test 3: Available Databases"
DATABASES=$(curl -s "http://localhost:8086/query?u=zmq&p=zmq&q=SHOW%20DATABASES" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print([v[0] for r in data['results'] for s in r.get('series',[]) for v in s.get('values',[])])" 2>/dev/null)
if [[ ! -z "$DATABASES" ]]; then
    print_pass "Databases found: $DATABASES"
else
    print_fail "Could not retrieve databases"
fi

# Test 4: Line Protocol Write
echo ""
echo "📋 Test 4: Line Protocol Write Endpoint"
WRITE_RESULT=$(curl -s -w "%{http_code}" -o /tmp/write_response.txt -X POST "http://localhost:8086/write?u=zmq&p=zmq&db=tick" \
  -d "test,location=us-west value=42.0 $(date +%s)000000000")
HTTP_CODE=${WRITE_RESULT: -3}

if [[ "$HTTP_CODE" == "204" ]] || [[ "$HTTP_CODE" == "200" ]]; then
    print_pass "Line protocol write successful (HTTP $HTTP_CODE)"
else
    print_fail "Line protocol write failed (HTTP $HTTP_CODE)"
    cat /tmp/write_response.txt
fi

# Test 5: Query Endpoint
echo ""
echo "📋 Test 5: Query Endpoint"
QUERY_RESULT=$(curl -s "http://localhost:8086/query?u=zmq&p=zmq&db=tick&q=SELECT%20COUNT(*%20)%20FROM%20test" 2>/dev/null)
if echo "$QUERY_RESULT" | grep -q "results"; then
    print_pass "Query endpoint responding with valid JSON"
    echo "   Response preview:"
    echo "$QUERY_RESULT" | python3 -m json.tool 2>/dev/null | head -15 | sed 's/^/   /'
else
    print_fail "Query endpoint failed"
fi

# Test 6: Port Binding
echo ""
echo "📋 Test 6: Port Binding Status"
PORT_CHECK=$(sudo ss -tlnp 2>/dev/null | grep 8086)
if [[ ! -z "$PORT_CHECK" ]]; then
    print_pass "Port 8086 is bound and listening"
    echo "   $PORT_CHECK" | sed 's/^/   /'
else
    print_fail "Port 8086 not listening"
fi

# Test 7: Docker Container Status
echo ""
echo "📋 Test 7: Docker Container Status"
CONTAINER_STATUS=$(sudo docker-compose -f /home/textolytics/nbpy/db/docker-compose.yml ps --format "{{.Names}}: {{.Status}}" 2>/dev/null | grep influxdb)
if [[ ! -z "$CONTAINER_STATUS" ]]; then
    print_pass "Container running"
    echo "   $CONTAINER_STATUS" | sed 's/^/   /'
else
    print_fail "Container not found or not running"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Summary                                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "InfluxDB Service Details:"
echo "  • HTTP API:        http://localhost:8086"
echo "  • Username:        zmq"
echo "  • Password:        zmq"
echo "  • Default DB:      tick"
echo ""
echo "API Endpoints Available:"
echo "  • Ping:            http://localhost:8086/ping"
echo "  • Write:           http://localhost:8086/write"
echo "  • Query:           http://localhost:8086/query"
echo ""
echo "Example Commands:"
echo ""
echo "  Write (Line Protocol):"
echo '    curl -X POST "http://localhost:8086/write?u=zmq&p=zmq&db=tick" \\'
echo '      -d "tick,symbol=EURUSD bid=1.0856,ask=1.0858"'
echo ""
echo "  Query (InfluxQL):"
echo '    curl "http://localhost:8086/query?u=zmq&p=zmq&db=tick&q=SELECT%20*%20FROM%20tick"'
echo ""
echo "  InfluxDB CLI:"
echo "    influx -host localhost -port 8086 -username zmq -password zmq"
echo ""
echo "  Python Client:"
echo "    from influxdb import InfluxDBClient"
echo "    client = InfluxDBClient(host='localhost', port=8086, username='zmq', password='zmq', database='tick')"
echo ""
print_pass "All tests completed!"
