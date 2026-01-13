#!/bin/bash

# InfluxDB Service - Getting Started Guide
# Run this script to display a user-friendly getting started guide

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   InfluxDB Service - Getting Started                       ║
║                      for nbpy Project (localhost:8086)                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


📦 WHAT WAS CREATED
════════════════════════════════════════════════════════════════════════════

You now have a complete InfluxDB service infrastructure with:

  ✓ Core Python library (influxdb_service.py)
  ✓ Configuration management (config.py)
  ✓ ZMQ integration (zmq_influxdb_bridge.py)
  ✓ System service control (influxdb_service.sh)
  ✓ Docker support (docker-compose.yml, Dockerfile)
  ✓ Complete documentation
  ✓ Usage examples
  ✓ Verification tools


🚀 QUICK START (Choose One Option)
════════════════════════════════════════════════════════════════════════════

Option 1: Using System Service (Linux)
────────────────────────────────────────────────────────────────────────────

  Step 1: Change to db directory
    cd /home/textolytics/nbpy/db

  Step 2: Install InfluxDB (one-time)
    ./influxdb_service.sh install

  Step 3: Start the service
    ./influxdb_service.sh start

  Step 4: Initialize databases
    ./influxdb_service.sh init-db

  Step 5: Verify it's running
    ./influxdb_service.sh status

  Then access:
    - HTTP API: http://localhost:8086
    - Influx CLI: influx -host localhost -port 8086
    - Python: from nbpy.db import InfluxDBService


Option 2: Using Docker Compose (Recommended for quick start)
────────────────────────────────────────────────────────────────────────────

  Step 1: Change to db directory
    cd /home/textolytics/nbpy/db

  Step 2: Start services (InfluxDB + Grafana)
    docker-compose up -d

  Step 3: Verify they're running
    docker-compose ps

  Then access:
    - InfluxDB: http://localhost:8086
    - Grafana: http://localhost:3000 (admin/admin)
    - Python: from nbpy.db import InfluxDBService

  To stop:
    docker-compose down


Option 3: Manual Installation
────────────────────────────────────────────────────────────────────────────

  Follow the detailed guide:
    cat INFLUXDB_SETUP.md


📝 VERIFY INSTALLATION
════════════════════════════════════════════════════════════════════════════

  Run the verification script:
    python3 simple_verify.py

  This will check:
    ✓ Python dependencies installed
    ✓ All module files present
    ✓ Shell scripts executable
    ✓ Documentation complete
    ✓ Docker files ready
    ✓ InfluxDB service running (if started)


💻 PYTHON USAGE EXAMPLES
════════════════════════════════════════════════════════════════════════════

Basic Usage:
────────────

    from nbpy.db import InfluxDBService, TickData

    service = InfluxDBService()

    # Write tick data
    tick = TickData(
        instrument="EURUSD",
        bid=1.0856,
        ask=1.0858,
        base_ccy="EUR",
        term_ccy="USD"
    )

    service.write_point(tick)
    service.flush(force=True)

    # Query data
    latest = service.get_latest_tick("EURUSD")
    print(latest)

    service.close()


ZMQ Integration:
────────────────

    from nbpy.db import create_kraken_bridge

    # Start collecting Kraken data
    bridge = create_kraken_bridge(zmq_port=5558)
    bridge.run(blocking=False)

    # Data automatically stored to InfluxDB
    # View statistics
    stats = bridge.get_stats()
    print(stats)


Run Examples:
─────────────

    python3 examples.py


📊 COMMAND REFERENCE
════════════════════════════════════════════════════════════════════════════

Service Control:
────────────────

    ./influxdb_service.sh start           # Start service
    ./influxdb_service.sh stop            # Stop service
    ./influxdb_service.sh status          # Check status
    ./influxdb_service.sh restart         # Restart service
    ./influxdb_service.sh logs            # View recent logs
    ./influxdb_service.sh follow          # Follow live logs
    ./influxdb_service.sh init-db         # Initialize databases
    ./influxdb_service.sh config          # Show configuration
    ./influxdb_service.sh help            # Show help


Docker Control:
───────────────

    docker-compose up -d                  # Start all services
    docker-compose down                   # Stop all services
    docker-compose ps                     # Show status
    docker-compose logs -f influxdb       # View logs
    docker-compose restart influxdb       # Restart InfluxDB


Accessing Data:
───────────────

    # HTTP API
    curl http://localhost:8086/ping

    # InfluxDB CLI
    influx -host localhost -port 8086
    > SHOW DATABASES
    > USE tick
    > SELECT * FROM tick LIMIT 10

    # Python
    python3 -c "from nbpy.db import InfluxDBService; s = InfluxDBService(); print(s.get_stats())"


📁 IMPORTANT FILES
════════════════════════════════════════════════════════════════════════════

Documentation:
    README.md                    - Module documentation
    INFLUXDB_SETUP.md           - Detailed setup guide
    QUICK_REFERENCE.md          - Quick command reference
    INFLUXDB_SERVICE_SUMMARY.md - This summary

Python Modules:
    influxdb_service.py         - Core service (20 KB)
    config.py                   - Configuration (11 KB)
    zmq_influxdb_bridge.py      - ZMQ integration (12 KB)

Scripts:
    influxdb_service.sh         - Service control
    init-databases.sh           - Database setup
    simple_verify.py            - Verification script
    examples.py                 - Usage examples

Docker:
    docker-compose.yml          - Docker Compose config
    Dockerfile                  - Custom image
    influxdb.service            - Systemd unit

Defaults:
    /etc/influxdb/influxdb.conf - Configuration file
    /var/lib/influxdb/          - Data directory
    /var/log/influxdb/          - Log files


⚙️  CONFIGURATION
════════════════════════════════════════════════════════════════════════════

Using Environment Variables:
────────────────────────────

    export INFLUXDB_HOST=localhost
    export INFLUXDB_PORT=8086
    export INFLUXDB_USER=zmq
    export INFLUXDB_PASSWORD=zmq
    export INFLUXDB_DB=tick


Using Configuration File (.env):
─────────────────────────────────

    Create .env file in /home/textolytics/nbpy/db/:

    INFLUXDB_HOST=localhost
    INFLUXDB_PORT=8086
    INFLUXDB_USER=zmq
    INFLUXDB_DB=tick


Using Python Code:
──────────────────

    from nbpy.db import InfluxDBConfig, InfluxDBService

    config = InfluxDBConfig(
        host="localhost",
        port=8086,
        database="tick",
        batch_size=500
    )

    service = InfluxDBService(config)


🔍 TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════

Problem: "Connection refused"
Solution: InfluxDB is not running. Start it:
    ./influxdb_service.sh start
    OR
    docker-compose up -d

Problem: "Port 8086 already in use"
Solution: Check what's using it:
    lsof -i :8086
  Then stop the service or use a different port

Problem: "Database not found"
Solution: Initialize databases:
    ./influxdb_service.sh init-db

Problem: "Module not found"
Solution: Install dependencies:
    pip install influxdb pyzmq

Problem: "Docker service won't start"
Solution: Check logs:
    docker-compose logs influxdb


📚 MORE INFORMATION
════════════════════════════════════════════════════════════════════════════

Quick Reference:
    cat QUICK_REFERENCE.md

Complete Setup Guide:
    cat INFLUXDB_SETUP.md

Module Documentation:
    cat README.md

Python Examples:
    python3 examples.py

Verify Setup:
    python3 simple_verify.py


🌐 ENDPOINTS
════════════════════════════════════════════════════════════════════════════

Service:
    InfluxDB HTTP API: http://localhost:8086
    Grafana (Docker):  http://localhost:3000

API Endpoints:
    Query:    http://localhost:8086/query
    Write:    http://localhost:8086/write
    Ping:     http://localhost:8086/ping


📊 DATABASES
════════════════════════════════════════════════════════════════════════════

Automatically created:

    tick            - Market tick data (bid/ask) - 30 day retention
    ohlc            - Candlestick data - 1 year retention
    depth           - Order book depth - 7 day retention
    orders          - Trading orders - 90 day retention
    sentiment       - Market sentiment - 30 day retention
    _internal       - InfluxDB metrics - auto retention


✓ YOU'RE ALL SET!
════════════════════════════════════════════════════════════════════════════

The InfluxDB service infrastructure is complete and ready to use.

Next Steps:
    1. Start InfluxDB:
       cd /home/textolytics/nbpy/db
       ./influxdb_service.sh start
       (OR: docker-compose up -d)

    2. Verify it's working:
       python3 simple_verify.py

    3. Try an example:
       python3 examples.py

    4. Read the documentation:
       cat README.md
       cat QUICK_REFERENCE.md

    5. Integrate with your ZMQ pipeline:
       from nbpy.db import create_kraken_bridge
       bridge = create_kraken_bridge()
       bridge.run()

Questions? Check the documentation files in this directory!


════════════════════════════════════════════════════════════════════════════
Generated: 2026-01-13
Location: /home/textolytics/nbpy/db/
Version: 1.0.0
Status: ✓ Production Ready
════════════════════════════════════════════════════════════════════════════

EOF
