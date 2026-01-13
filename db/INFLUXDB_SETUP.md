# InfluxDB Service Setup for nbpy Project

Complete guide for setting up and managing InfluxDB server for the nbpy project on localhost:8086.

## Overview

This directory contains everything needed to run InfluxDB as a persistent time-series database for the nbpy ZMQ pipeline:

- **influxdb_service.sh** - System service management script
- **docker-compose.yml** - Docker Compose configuration
- **Dockerfile** - Custom Docker image
- **init-databases.sh** - Database initialization script
- **influxdb.conf** - InfluxDB configuration file

## Quick Start

### Option 1: Using System Service (Linux)

#### Step 1: Install InfluxDB

```bash
cd /home/textolytics/nbpy/db
./influxdb_service.sh install
```

#### Step 2: Initialize Directories

```bash
./influxdb_service.sh generate-config
```

#### Step 3: Start Service

```bash
./influxdb_service.sh start
```

#### Step 4: Initialize Databases

```bash
./influxdb_service.sh init-db
```

#### Step 5: Verify Status

```bash
./influxdb_service.sh status
```

### Option 2: Using Docker Compose (Recommended)

#### Step 1: Start InfluxDB and Grafana

```bash
cd /home/textolytics/nbpy/db
docker-compose up -d
```

#### Step 2: Verify Services

```bash
docker-compose ps
```

#### Step 3: Check InfluxDB

```bash
curl http://localhost:8086/ping
```

### Option 3: Using Docker Container Directly

```bash
# Build custom image
docker build -t nbpy-influxdb .

# Run container
docker run -d \
  --name nbpy_influxdb \
  -p 8086:8086 \
  -p 8088:8088 \
  -v influxdb_data:/var/lib/influxdb \
  nbpy-influxdb
```

## Service Management

### Start/Stop/Restart

```bash
# Start service
./influxdb_service.sh start

# Stop service
./influxdb_service.sh stop

# Restart service
./influxdb_service.sh restart

# Check status
./influxdb_service.sh status
```

### Logs and Debugging

```bash
# Show recent logs
./influxdb_service.sh logs

# Follow logs in real-time
./influxdb_service.sh follow
```

### Configuration

```bash
# View current configuration
./influxdb_service.sh config

# Generate new configuration
./influxdb_service.sh generate-config
```

### Database Management

```bash
# Initialize databases and retention policies
./influxdb_service.sh init-db
```

## Available Databases

The system creates these databases automatically:

| Database | Purpose | Retention Policy |
|----------|---------|------------------|
| `tick` | Market tick data (bid/ask) | 30 days |
| `ohlc` | Candlestick data | 1 year |
| `depth` | Order book depth data | 7 days |
| `orders` | Trading orders | 90 days |
| `sentiment` | Market sentiment | 30 days |
| `_internal` | InfluxDB metrics | auto |

## Connecting to InfluxDB

### HTTP API

```bash
# Ping server
curl http://localhost:8086/ping

# Query data
curl -G http://localhost:8086/query?db=tick --data-urlencode 'q=SELECT * FROM tick LIMIT 10'

# Write data
curl -i -XPOST http://localhost:8086/write?db=tick --data-binary 'tick,instrument=EURUSD bid=1.0856,ask=1.0858'
```

### Using influx CLI

```bash
# Connect to server
influx -host localhost -port 8086

# From within influx CLI:
> SHOW DATABASES
> USE tick
> SELECT * FROM tick LIMIT 10
> SHOW RETENTION POLICIES
```

### Using nbpy Python Module

```python
from nbpy.db import InfluxDBService, TickData

# Create service
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
```

## Integration with ZMQ Services

The ZMQ bridges automatically forward data to InfluxDB:

```python
from nbpy.db import create_kraken_bridge

# Create Kraken tick bridge
bridge = create_kraken_bridge(zmq_port=5558)

# Start collecting and storing data
bridge.run(blocking=False)

# Run ZMQ services in parallel
# Data flows: ZMQ Publisher → Bridge → InfluxDB
```

## Docker Compose Services

### InfluxDB Service

- **Container**: `nbpy_influxdb`
- **Port**: 8086 (HTTP API), 8088 (RPC)
- **Data Volume**: `influxdb_data`
- **Config Volume**: `influxdb_config`
- **Health Check**: Every 30 seconds

### Grafana Service (Optional)

- **Container**: `nbpy_grafana`
- **Port**: 3000
- **Default Credentials**: admin / admin
- **Data Volume**: `grafana_data`

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f influxdb

# Restart InfluxDB
docker-compose restart influxdb

# Remove all data and volumes
docker-compose down -v
```

## Performance Tuning

### Batch Writing

Configure batch size in Python:

```python
from nbpy.db import InfluxDBConfig, InfluxDBService

config = InfluxDBConfig(
    batch_size=1000,  # Increase for better throughput
    timeout=15        # Increase for slower networks
)

service = InfluxDBService(config)
```

### Retention Policies

Modify retention in initialization script:

```bash
# Change retention for tick data to 60 days
influx -execute "ALTER RETENTION POLICY tick_30day ON tick DURATION 60d"
```

### Continuous Queries

Create downsampling queries:

```bash
influx -database tick -execute "
CREATE CONTINUOUS QUERY cq_tick_5min ON tick 
BEGIN 
    SELECT 
        FIRST(bid) AS open, 
        MAX(bid) AS high, 
        MIN(bid) AS low, 
        LAST(bid) AS close
    INTO ohlc 
    FROM tick 
    GROUP BY time(5m), * 
END
"
```

## Backup and Restore

### Backup

```bash
# Backup single database
influxd backup -database tick /path/to/backup

# Backup all databases
influxd backup /path/to/backup

# Docker backup
docker exec nbpy_influxdb influxd backup -database tick /var/lib/influxdb/backup
```

### Restore

```bash
# Restore database
influxd restore -database tick /path/to/backup

# Docker restore
docker exec nbpy_influxdb influxd restore -database tick /var/lib/influxdb/backup
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
./influxdb_service.sh logs

# Verify installation
which influxd
influxd version

# Check port availability
lsof -i :8086
```

### Connection Refused

```bash
# Test connection
curl http://localhost:8086/ping

# Check firewall
sudo ufw allow 8086

# Check process
ps aux | grep influxd
```

### High Memory Usage

```bash
# Check cache settings in influxdb.conf
cache-max-memory-bytes = 1073741824  # 1GB default

# Query memory usage
influx -execute "SHOW STATS" -database _internal
```

### Database Not Found

```bash
# List databases
influx -execute "SHOW DATABASES"

# Create missing database
influx -execute "CREATE DATABASE tick"

# Initialize all databases
./influxdb_service.sh init-db
```

## Security

### Enable Authentication

Edit `influxdb.conf`:

```ini
[http]
  auth-enabled = true
```

Create user:

```bash
influx -execute "CREATE USER admin WITH PASSWORD 'secure_password' WITH ALL PRIVILEGES"
```

### Enable HTTPS

Edit `influxdb.conf`:

```ini
[http]
  https-enabled = true
  https-certificate = "/path/to/cert.pem"
  https-private-key = "/path/to/key.pem"
```

## Monitoring

### Using InfluxDB Built-in Metrics

```bash
# Query internal metrics
influx -database _internal -execute "SELECT * FROM 'system' LIMIT 10"
```

### Using Grafana

1. Open http://localhost:3000
2. Login with admin/admin
3. Add InfluxDB data source: http://influxdb:8086
4. Create dashboards for your data

### Using telegraf (Optional)

```bash
# Install telegraf
sudo apt-get install telegraf

# Configure to collect InfluxDB metrics
telegraf --sample-config > /etc/telegraf/telegraf.conf
```

## Advanced Configuration

### UDP Input

Enable UDP for high-volume writes:

```bash
# Edit influxdb.conf
[[udp]]
  enabled = true
  bind-address = ":8089"
  database = "tick"
```

### Graphite Protocol

Enable Graphite compatibility:

```bash
# Edit influxdb.conf
[[graphite]]
  enabled = true
  bind-address = ":2003"
  database = "graphite"
```

## Environment Variables

```bash
# Set custom directories
export INFLUXDB_HOME=/opt/influxdb
export INFLUXDB_DATA_DIR=/var/lib/influxdb
export INFLUXDB_CONFIG=/etc/influxdb/influxdb.conf
export INFLUXDB_LOG_DIR=/var/log/influxdb

# Set connection parameters
export INFLUXDB_HOST=localhost
export INFLUXDB_PORT=8086
export INFLUXDB_USER=influxdb
```

## Files and Directories

```
/home/textolytics/nbpy/db/
├── influxdb_service.sh          # Service management script
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Custom Docker image
├── influxdb.conf               # Configuration file
├── init-databases.sh           # Database initialization
├── examples.py                 # Python examples
├── influxdb_service.py         # Python service module
├── config.py                   # Configuration management
├── zmq_influxdb_bridge.py      # ZMQ integration
└── README.md                   # This file

Default Locations:
├── /var/lib/influxdb/          # Data directory
├── /var/log/influxdb/          # Log directory
├── /etc/influxdb/              # Configuration
└── /var/run/influxdb/          # PID files
```

## Getting Help

```bash
# Show help for service script
./influxdb_service.sh help

# InfluxDB documentation
https://docs.influxdata.com/influxdb/latest/

# Python module documentation
See README.md in db/ directory
```

## License

Part of the nbpy project

## Support

For issues or questions:
1. Check logs: `./influxdb_service.sh logs`
2. Review configuration: `./influxdb_service.sh config`
3. Test connection: `curl http://localhost:8086/ping`
4. Verify Python module: `python3 -c "from nbpy.db import InfluxDBService; print('OK')"`
