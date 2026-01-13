#!/bin/bash

# Quick Reference for InfluxDB Service
# Print this with: ./QUICK_REFERENCE.md or cat QUICK_REFERENCE.md

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════════╗
║                  InfluxDB Service - Quick Reference                       ║
║                  localhost:8086                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📋 QUICK COMMANDS
═══════════════════════════════════════════════════════════════════════════

  # System Service (Linux)
  ./influxdb_service.sh start              # Start service
  ./influxdb_service.sh stop               # Stop service
  ./influxdb_service.sh status             # Check status
  ./influxdb_service.sh restart            # Restart service
  ./influxdb_service.sh logs               # View logs
  ./influxdb_service.sh follow             # Follow logs live
  ./influxdb_service.sh init-db            # Initialize databases

  # Docker Compose
  docker-compose up -d                     # Start with Docker
  docker-compose down                      # Stop containers
  docker-compose logs -f                   # View logs

🔧 SYSTEM SETUP
═══════════════════════════════════════════════════════════════════════════

  1. Install InfluxDB
     ./influxdb_service.sh install

  2. Generate Configuration
     ./influxdb_service.sh generate-config

  3. Start Service
     ./influxdb_service.sh start

  4. Initialize Databases
     ./influxdb_service.sh init-db

  5. Verify Status
     ./influxdb_service.sh status

  OR Use Docker Compose:
     docker-compose up -d

🐳 DOCKER SETUP
═══════════════════════════════════════════════════════════════════════════

  # Start all services (InfluxDB + Grafana)
  docker-compose up -d

  # Check services
  docker-compose ps

  # View InfluxDB logs
  docker-compose logs -f influxdb

  # Access services
  InfluxDB:   http://localhost:8086
  Grafana:    http://localhost:3000
  Grafana:    admin / admin (default password)

📊 DATABASES
═══════════════════════════════════════════════════════════════════════════

  Database     | Purpose              | Retention
  ─────────────┼──────────────────────┼─────────────
  tick         | Market tick data     | 30 days
  ohlc         | Candlestick data     | 1 year
  depth        | Order book depth     | 7 days
  orders       | Trading orders       | 90 days
  sentiment    | Market sentiment     | 30 days
  _internal    | InfluxDB metrics     | auto

🔗 CONNECTIONS
═══════════════════════════════════════════════════════════════════════════

  HTTP API:
    curl http://localhost:8086/ping

  InfluxDB CLI:
    influx -host localhost -port 8086

  Python Client:
    from nbpy.db import InfluxDBService
    service = InfluxDBService()

  ZMQ Bridge:
    from nbpy.db import create_kraken_bridge
    bridge = create_kraken_bridge(zmq_port=5558)
    bridge.run(blocking=False)

💾 DATA OPERATIONS
═══════════════════════════════════════════════════════════════════════════

  # Write data with Python
  from nbpy.db import TickData, create_service
  
  with create_service() as service:
      tick = TickData(instrument="EURUSD", bid=1.0856, ask=1.0858)
      service.write_point(tick)
      service.flush(force=True)

  # Write data with HTTP
  curl -i -XPOST http://localhost:8086/write?db=tick \
    --data-binary 'tick,instrument=EURUSD bid=1.0856,ask=1.0858'

  # Query data
  influx -database tick -execute "SELECT * FROM tick LIMIT 10"

  # Query from Python
  latest = service.get_latest_tick("EURUSD")
  ohlc = service.get_ohlc("EURUSD", hours=24)

🔍 MONITORING
═══════════════════════════════════════════════════════════════════════════

  # Service Status
  ./influxdb_service.sh status

  # Recent Logs
  ./influxdb_service.sh logs

  # Follow Live Logs
  ./influxdb_service.sh follow

  # Service Statistics
  influx -database _internal -execute "SHOW STATS"

  # Check Disk Usage
  du -sh /var/lib/influxdb

🛠 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

  Problem                  | Solution
  ────────────────────────┼──────────────────────────────────
  Connection refused      | ./influxdb_service.sh status
  Port 8086 in use        | lsof -i :8086
  High memory usage       | Check influxdb.conf cache settings
  Database not found      | ./influxdb_service.sh init-db
  Authentication error    | Check credentials in config.py
  Docker container fails  | docker-compose logs influxdb

  # Test connectivity
  curl http://localhost:8086/ping

  # Check if running
  ps aux | grep influxd

  # Check logs
  ./influxdb_service.sh logs | tail -50

📁 FILE LOCATIONS
═══════════════════════════════════════════════════════════════════════════

  Scripts:
    ./influxdb_service.sh              System service control
    ./init-databases.sh                Database initialization
    ./docker-compose.yml               Docker configuration
    ./Dockerfile                       Custom Docker image

  Configuration:
    /etc/influxdb/influxdb.conf       Server configuration
    ./influxdb.service                Systemd service unit

  Data:
    /var/lib/influxdb/                Database files
    /var/log/influxdb/                Log files
    /var/run/influxdb/                PID and runtime files

  Python:
    ./influxdb_service.py             Service module
    ./zmq_influxdb_bridge.py          ZMQ integration
    ./config.py                       Configuration management

📚 SYSTEMD INTEGRATION
═══════════════════════════════════════════════════════════════════════════

  # Install service unit
  sudo cp influxdb.service /etc/systemd/system/
  sudo systemctl daemon-reload

  # Service management
  sudo systemctl start influxdb
  sudo systemctl stop influxdb
  sudo systemctl restart influxdb
  sudo systemctl status influxdb

  # Enable on boot
  sudo systemctl enable influxdb

  # View logs
  sudo journalctl -u influxdb -f

🚀 ADVANCED USAGE
═══════════════════════════════════════════════════════════════════════════

  # Backup
  influxd backup -database tick /path/to/backup

  # Restore
  influxd restore -database tick /path/to/backup

  # Configure High Availability (multiple nodes)
  Edit influxdb.conf [meta] section

  # Enable continuous queries
  CREATE CONTINUOUS QUERY cq_name ON database_name
  BEGIN ... END

  # Create custom retention policies
  CREATE RETENTION POLICY "rp_name" ON "db_name" 
    DURATION 30d REPLICATION 1 DEFAULT

🌐 ENDPOINTS
═══════════════════════════════════════════════════════════════════════════

  HTTP API:      http://localhost:8086
  Query:         http://localhost:8086/query
  Write:         http://localhost:8086/write
  Ping:          http://localhost:8086/ping
  
  Docker:
    InfluxDB:    http://localhost:8086
    Grafana:     http://localhost:3000

📖 DOCUMENTATION
═══════════════════════════════════════════════════════════════════════════

  Online:
    https://docs.influxdata.com/influxdb/latest/

  Local:
    ./README.md                        Module overview
    ./INFLUXDB_SETUP.md               Detailed setup guide
    ./INTEGRATION_GUIDE.md            Integration examples
    ./QUICKSTART.md                   Quick start guide

ℹ️  HELP & SUPPORT
═══════════════════════════════════════════════════════════════════════════

  Script help:
    ./influxdb_service.sh help

  InfluxDB help:
    influx -help
    influxd -help

  Check module imports:
    python3 -c "from nbpy.db import *; print('✓ OK')"

═══════════════════════════════════════════════════════════════════════════

Version: 1.0.0
Last Updated: 2026-01-13
Status: ✓ Production Ready

═══════════════════════════════════════════════════════════════════════════

EOF
