#!/bin/bash
#
# Start All Docker Services (InfluxDB + Grafana)
# This script starts both InfluxDB and Grafana containers
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Starting nbpy Docker Services"
echo "=========================================="
echo ""

# Start both services
echo "[*] Starting Docker containers..."
sudo docker-compose up -d

echo "[✓] Containers started"
echo ""

# Wait for services to be ready
echo "[*] Waiting for services to be ready..."
sleep 5

# Check InfluxDB health
echo "[*] Checking InfluxDB health..."
if curl -s http://localhost:8086/health > /dev/null 2>&1; then
    echo "[✓] InfluxDB is ready at http://localhost:8086"
else
    echo "[!] InfluxDB is starting up..."
fi

# Check Grafana health
echo "[*] Checking Grafana health..."
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "[✓] Grafana is ready at http://localhost:3000"
else
    echo "[!] Grafana is starting up..."
fi

echo ""
echo "=========================================="
echo "Services Summary"
echo "=========================================="
echo ""
echo "InfluxDB:"
echo "  URL:      http://localhost:8086"
echo "  Username: admin"
echo "  Password: adminpassword"
echo ""
echo "Grafana:"
echo "  URL:      http://localhost:3000"
echo "  Username: admin"
echo "  Password: adminpassword"
echo ""
echo "To view logs:"
echo "  InfluxDB:  sudo docker logs -f nbpy_influxdb"
echo "  Grafana:   sudo docker logs -f nbpy_grafana"
echo ""
echo "To stop services:"
echo "  cd $SCRIPT_DIR && sudo docker-compose down"
echo ""
