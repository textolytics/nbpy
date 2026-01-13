# NBPY Integrated Startup - Quick Reference

Complete integration of db and nbpy modules with graceful orchestration, real-time monitoring, and data persistence.

## Quick Start (30 seconds)

```bash
cd /home/textolytics/nbpy

# Start everything at once
./integrated_startup.sh start

# When done, gracefully stop
./integrated_startup.sh stop
```

## What Gets Started

```
Phase 1: Docker Containers (InfluxDB + Grafana)
   ↓
Phase 2: InfluxDB Retention Policies (30d, 7d, 365d)
   ↓
Phase 3: ZMQ Publishers (5 data sources streaming)
   ↓
Phase 4: Grafana Dashboards (auto-provisioned)
   ↓
Phase 5: Message Validation (verify data flow)
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **InfluxDB API** | http://localhost:8086 | zmq / zmq |
| **Kraken Tick** | tcp://localhost:5558 | ZMQ PUB |
| **Kraken Depth** | tcp://localhost:5560 | ZMQ PUB |
| **OANDA Tick** | tcp://localhost:5562 | ZMQ PUB |
| **Betfair Stream** | tcp://localhost:5564 | ZMQ PUB |

## Key Commands

### System Management
```bash
./integrated_startup.sh start      # Start everything
./integrated_startup.sh stop       # Graceful shutdown
./integrated_startup.sh restart    # Restart all
./integrated_startup.sh status     # Show status
./integrated_startup.sh validate   # Verify message flow
```

### Service Management
```bash
python3 db/service_manager.py --config integration_config.json start
python3 db/service_manager.py --config integration_config.json stop
python3 db/service_manager.py --config integration_config.json status
python3 db/service_manager.py --config integration_config.json monitor
```

### InfluxDB Management
```bash
# Create/verify retention policies
python3 db/retention_policy.py --config integration_config.json create

# View retention policies
python3 db/retention_policy.py --config integration_config.json list

# Show database statistics
python3 db/retention_policy.py --config integration_config.json stats

# Cleanup old data
python3 db/retention_policy.py --config integration_config.json cleanup
```

### Message Validation
```bash
# Validate ZMQ message streaming
python3 db/message_validator.py --config integration_config.json zmq

# Validate InfluxDB data ingestion
python3 db/message_validator.py --config integration_config.json influxdb

# Full validation (ZMQ + InfluxDB)
python3 db/message_validator.py --config integration_config.json full
```

### Grafana Setup
```bash
# Full setup
python3 db/grafana_setup.py --config integration_config.json setup

# Only datasource
python3 db/grafana_setup.py --config integration_config.json datasource

# Only dashboards
python3 db/grafana_setup.py --config integration_config.json dashboards
```

### Health Monitoring
```bash
# One-time health check
python3 db/health_check.py --config integration_config.json check

# Continuous monitoring (30s intervals)
python3 db/health_check.py --config integration_config.json monitor
```

## Docker Commands

```bash
# View container status
docker-compose ps

# View logs
docker-compose logs -f influxdb
docker-compose logs -f grafana

# Stop containers
docker-compose down

# View volumes
docker volume ls
```

## Log Files

```bash
logs/integrated_startup.log     # Main startup log
logs/service_manager.log        # Service lifecycle
logs/message_validator.log      # Message validation
logs/retention_policy.log       # InfluxDB setup
logs/grafana_setup.log          # Grafana provisioning
logs/health_check.log           # Health monitoring
logs/kraken_tick.log            # Publisher/Subscriber logs
```

## System Architecture

```
Publishers (Kraken, OANDA, Betfair, Twitter)
        ↓
     ZMQ Topics (tcp://localhost:555x)
        ↓
Subscribers (Listen to ZMQ)
        ↓
    InfluxDB (Persist to 'tick' database)
        ↓
     Grafana (Visualize dashboards)
```

## Expected Startup Output

```
[INFO] ✓ Docker services started
[INFO] ✓ InfluxDB is healthy
[INFO] ✓ Grafana is healthy
[INFO] ✓ Retention policies configured
[INFO] ✓ Publishers started
[INFO] ✓ Grafana dashboards provisioned
[INFO] ✓ Validation: ALL TOPICS STREAMING SUCCESSFULLY
[SUCCESS] System startup complete

Access Points:
  InfluxDB API        → http://localhost:8086
  Grafana UI          → http://localhost:3000
```

## Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Kill process using the port
sudo lsof -i :8086    # Find what's using port 8086
kill -9 <PID>
```

### Issue: "No messages in InfluxDB"
```bash
# Check if publishers are running
ps aux | grep publisher

# Monitor topic directly
python3 db/message_validator.py zmq --duration 20

# Check subscriber logs
tail -f logs/kraken_influxdb_tick.log
```

### Issue: "Graceful shutdown timeout"
```bash
# Force stop
pkill -f "kraken_tick"
docker-compose down --force-remove-volumes
```

### Issue: "Grafana dashboards empty"
```bash
# Verify datasource
curl -u admin:admin123 http://localhost:3000/api/datasources

# Check if InfluxDB has data
python3 db/retention_policy.py stats
```

## Performance Monitoring

```bash
# Real-time system stats
watch -n 1 'docker stats --no-stream'

# Monitor disk usage
df -h /var/lib/docker/volumes/

# Check network traffic
nethogs

# Database statistics
python3 db/retention_policy.py stats
```

## Database Queries

```bash
# Query InfluxDB directly
influx -host localhost -port 8086 -username zmq -password zmq -database tick

# List measurements
> SHOW MEASUREMENTS

# Query kraken_tick data
> SELECT * FROM kraken_tick LIMIT 10

# Get data count
> SELECT COUNT(*) FROM kraken_tick

# Get latest data
> SELECT * FROM kraken_tick ORDER BY time DESC LIMIT 1
```

## Configuration Files

| File | Purpose |
|------|---------|
| `integration_config.json` | Central configuration for all services |
| `docker-compose.yml` | Docker container definitions |
| `.env` | Environment variables (if using .env) |
| `conf/` | Configuration templates |
| `db/config.py` | Python InfluxDB config |
| `nbpy/zmq/ports.py` | ZMQ port definitions |

## File Structure

```
/home/textolytics/nbpy/
├── integrated_startup.sh          # Main startup script
├── INTEGRATION_STARTUP.md         # Full documentation
├── QUICK_START.md                 # This file
├── integration_config.json        # System configuration
├── docker-compose.yml             # Docker services
├── logs/
│   ├── integrated_startup.log
│   ├── service_manager.log
│   ├── message_validator.log
│   └── ...
├── db/
│   ├── service_manager.py         # Service lifecycle
│   ├── retention_policy.py        # InfluxDB policies
│   ├── message_validator.py       # Message validation
│   ├── grafana_setup.py           # Grafana provisioning
│   └── health_check.py            # Health monitoring
└── nbpy/
    └── zmq/
        ├── publishers/            # Data source publishers
        └── subscribers/           # Data sink subscribers
```

## Retention Policies

Three retention policies are automatically created:

| Policy | Duration | Shard Duration | Use Case |
|--------|----------|----------------|----------|
| **default** | 30 days | 1 day | Standard data |
| **high_frequency** | 7 days | 6 hours | Recent high-resolution |
| **long_term** | 365 days | 30 days | Long-term archival |

## ZMQ Topics & Publishers

| Topic | Publisher | Port | Data Type |
|-------|-----------|------|-----------|
| kraken_tick | KrakenTickPublisher | 5558 | Market ticks |
| kraken_depth | KrakenDepthPublisher | 5560 | Order book |
| kraken_orders | KrakenOrdersPublisher | 5561 | Trades |
| oanda_tick | OandaTickPublisher | 5562 | FX ticks |
| betfair_stream | BetfairStreamPublisher | 5564 | Betting odds |

## Measurements in InfluxDB

```
kraken_tick         → bid, ask, last_trade_price, volume, vwap
kraken_depth        → bid_price, bid_size, ask_price, ask_size
kraken_orders       → order_id, price, amount
oanda_tick          → bid, ask, volume
betfair_stream      → back_price, lay_price, matched_amount
```

## Python API Examples

### Query InfluxDB
```python
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086, 
                       username='zmq', password='zmq',
                       database='tick')

# Query data
result = client.query('SELECT * FROM kraken_tick LIMIT 10')
for point in result.get_points():
    print(point)
```

### Access ZMQ Topics
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5558')
socket.setsockopt_string(zmq.SUBSCRIBE, 'kraken_tick')

# Receive messages
while True:
    message = socket.recv_multipart()
    print(f"Received: {message}")
```

## Grafana Dashboard Overview

Five dashboards are automatically created:

1. **Kraken Tick Stream** - Real-time market data
2. **Kraken Depth Stream** - Order book levels
3. **Kraken Orders Stream** - Trade execution
4. **OANDA Tick Stream** - FX market data
5. **Betfair Stream** - Betting market data

Each dashboard includes:
- Time-series graphs (1-hour window)
- Latest value statistics
- Raw data tables
- 5-second refresh rate

## Support & Resources

- **Full Documentation**: [INTEGRATION_STARTUP.md](INTEGRATION_STARTUP.md)
- **Configuration Details**: [integration_config.json](integration_config.json)
- **Source Code**: [db/](db/) and [nbpy/zmq/](nbpy/zmq/)
- **Logs**: Check [logs/](logs/) directory

## Key Features Implemented

✅ **Graceful Startup** - Orchestrated 5-phase startup with health checks
✅ **Graceful Shutdown** - 30-second timeout for clean termination
✅ **Docker Integration** - InfluxDB + Grafana in containers
✅ **Retention Policies** - 3 configurable policies (7d, 30d, 365d)
✅ **ZMQ Publishers** - 5 data source publishers with proper error handling
✅ **ZMQ Subscribers** - Automatic data forwarding to InfluxDB
✅ **Message Validation** - Verify data flow through entire pipeline
✅ **Grafana Dashboards** - Auto-provisioned for each topic
✅ **Health Monitoring** - Continuous system health checks
✅ **Comprehensive Logging** - Detailed logs for all components

---

**Last Updated**: January 2026
**Status**: Production Ready
