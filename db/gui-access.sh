#!/bin/bash

# InfluxDB 2.x GUI Access Guide
# Opens the default InfluxDB GUI at port 8086

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           InfluxDB 2.x Web UI - Quick Start                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running
if ! curl -s http://localhost:8086 > /dev/null 2>&1; then
    echo "❌ InfluxDB is not running on port 8086"
    echo ""
    echo "To start InfluxDB:"
    echo "  cd /home/textolytics/nbpy/db"
    echo "  sudo docker-compose up -d"
    exit 1
fi

echo "✓ InfluxDB 2.x is running!"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Access Information                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Web UI URL:"
echo "   http://localhost:8086"
echo ""
echo "🔑 Login Credentials:"
echo "   Username: zmq"
echo "   Password: zmq"
echo ""
echo "📊 Organization:"
echo "   Name: nbpy"
echo "   Bucket: tick"
echo ""
echo "🔐 API Token:"
echo "   zmq-admin-token-secret"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Features Available                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "✓ Data Explorer - Query and visualize data"
echo "✓ Dashboards - Create custom dashboards"
echo "✓ Tasks - Automate workflows"
echo "✓ Alerts - Set up monitoring and alerts"
echo "✓ Admin Settings - Manage users and organizations"
echo "✓ API Documentation - Built-in API explorer"
echo "✓ InfluxQL/Flux Support - Query language support"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Quick Commands                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Write data (Line Protocol):"
echo '  curl -X POST "http://localhost:8086/api/v2/write?org=nbpy&bucket=tick" \\'
echo '    -H "Authorization: Token zmq-admin-token-secret" \\'
echo '    -d "tick,symbol=EURUSD bid=1.0856,ask=1.0858"'
echo ""
echo "Query data (Flux):"
echo '  curl -X POST "http://localhost:8086/api/v2/query?org=nbpy" \\'
echo '    -H "Authorization: Token zmq-admin-token-secret" \\'
echo '    -H "Content-Type: application/vnd.flux" \\'
echo '    -d "from(bucket:\"tick\") |> range(start: -1h)"'
echo ""
echo "Get API Token:"
echo '  curl -X GET "http://localhost:8086/api/v2/authorizations" \\'
echo '    -H "Authorization: Token zmq-admin-token-secret"'
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Python Client Example                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
cat << 'PYTHON'
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Initialize client
client = InfluxDBClient(
    url="http://localhost:8086",
    token="zmq-admin-token-secret",
    org="nbpy"
)

# Write data
write_api = client.write_api(write_options=SYNCHRONOUS)
line = "tick,symbol=EURUSD bid=1.0856,ask=1.0858"
write_api.write(bucket="tick", record=line)

# Query data
query_api = client.query_api()
flux = 'from(bucket:"tick") |> range(start: -1h)'
result = query_api.query(org="nbpy", query=flux)

for table in result:
    for record in table.records:
        print(record)

client.close()
PYTHON
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   Docker Commands                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "View logs:"
echo "  sudo docker-compose -f /home/textolytics/nbpy/db/docker-compose.yml logs -f influxdb"
echo ""
echo "Stop InfluxDB:"
echo "  sudo docker-compose -f /home/textolytics/nbpy/db/docker-compose.yml down"
echo ""
echo "Restart InfluxDB:"
echo "  sudo /home/textolytics/nbpy/db/docker-restart.sh"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║             ✓ Ready to Use!                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Open your browser and navigate to:"
echo "   👉 http://localhost:8086"
echo ""
