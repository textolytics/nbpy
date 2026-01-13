# NBPY Integrated ZMQ Microservices Orchestration System

Complete documentation for the integrated startup, monitoring, and graceful shutdown of the NBPY ZMQ microservices platform with InfluxDB persistence and Grafana visualization.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Detailed Startup Phases](#detailed-startup-phases)
5. [Configuration](#configuration)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

---

## System Overview

The NBPY Integrated System provides orchestrated startup and management of:

- **Docker Containers**: InfluxDB (time-series database) + Grafana (visualization)
- **ZMQ Publishers**: Data source microservices streaming market data
- **ZMQ Subscribers**: Data sink services consuming and forwarding to InfluxDB
- **InfluxDB**: Time-series data storage with retention policies
- **Grafana**: Real-time dashboards for monitoring data streams

### Key Features

✓ **Graceful Startup**: Services start in correct dependency order
✓ **Health Checks**: Automatic verification at each phase
✓ **Data Persistence**: InfluxDB with configurable retention policies
✓ **Real-time Visualization**: Grafana dashboards for each topic
✓ **Message Validation**: Verify data flow through complete pipeline
✓ **Graceful Shutdown**: Clean termination with timeout protection
✓ **Comprehensive Logging**: Detailed logs for debugging

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│              ZMQ Publishers (Data Sources)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Kraken   │  │  OANDA   │  │ Betfair  │  │ Twitter  │  │
│  │ Tick     │  │  Orders  │  │ Stream   │  │Sentiment │  │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘  │
│        │             │             │             │         │
│        └─────────────┴─────────────┴─────────────┘         │
│                      │                                      │
│                 ZMQ Network (localhost)                    │
│                      │                                      │
│        ┌─────────────┴─────────────┬───────────┐           │
│        │                           │           │           │
│   ┌────▼────┐    ┌──────────┐  ┌──▼────┐  ┌──▼────┐      │
│   │Kraken   │    │ OANDA    │  │ Data  │  │Grafana│      │
│   │InfluxDB │    │InfluxDB  │  │Filter │  │Setup  │      │
│   │Subscriber   │ Subscriber   │Publ.  │  │Engine │      │
│   └────┬────┘    └──────────┘  └──┬────┘  └───────┘      │
│        │                          │                        │
│        └──────────┬───────────────┘                        │
│                   │                                         │
│            ┌──────▼──────┐                                 │
│            │   InfluxDB  │                                 │
│            │   (Docker)  │                                 │
│            │             │                                 │
│            │ Tick DB     │                                 │
│            │ Measurements│                                 │
│            └──────┬──────┘                                 │
│                   │                                         │
│         ┌─────────┴──────────┐                             │
│         │                    │                             │
│    ┌────▼────┐         ┌────▼─────┐                       │
│    │ Grafana │         │Data Query │                       │
│    │Dashboards          │Analytics │                      │
│    │ (Port 3000)        │           │                      │
│    └─────────┘         └───────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Publisher → ZMQ Network → Subscriber → InfluxDB → Grafana
  ↓                        ↓             ↓
Messages             Forward data    Store           Display
on topics            to InfluxDB     Time-Series     in UI
                                     with Tags
```

---

## Quick Start

### 1. Prerequisites

```bash
# Install dependencies
sudo apt-get install docker docker-compose curl

# Create Python virtual environment
cd /home/textolytics/nbpy
python3 -m venv nbpy
source nbpy/bin/activate

# Install Python packages
pip install -e .
pip install msgpack influxdb pyzmq requests
```

### 2. Start the System

```bash
# From the nbpy directory
./integrated_startup.sh start
```

This will:
1. ✓ Start Docker containers (InfluxDB + Grafana)
2. ✓ Configure InfluxDB retention policies
3. ✓ Start ZMQ publishers
4. ✓ Provision Grafana dashboards
5. ✓ Validate message streaming
6. ✓ Display access information

### 3. Access the System

- **Grafana**: http://localhost:3000 (admin/admin123)
- **InfluxDB API**: http://localhost:8086
- **ZMQ Topics**: tcp://localhost:5558, 5560, 5562, etc.

### 4. Stop the System

```bash
./integrated_startup.sh stop
```

Gracefully shuts down all services with 30-second timeout.

---

## Detailed Startup Phases

### Phase 1: Docker Containers (15 seconds)

**What happens:**
- Pulls and starts InfluxDB 1.8 container
- Pulls and starts Grafana latest container
- Sets up docker volumes for persistence
- Configures environment variables

**Verification:**
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs influxdb
docker-compose logs grafana
```

**Expected Output:**
```
✓ InfluxDB is healthy
✓ Grafana is healthy
```

### Phase 2: InfluxDB Retention Policies (5 seconds)

**What happens:**
- Creates 'tick' database if needed
- Sets up three retention policies:
  - **default**: 30 days (standard data)
  - **high_frequency**: 7 days (aggressive retention)
  - **long_term**: 365 days (archival)

**Configuration:**
```json
{
  "name": "default",
  "duration": "30d",
  "replication": 1,
  "shard_duration": "1d"
}
```

**Verification:**
```bash
python3 db/retention_policy.py --config integration_config.json list
```

### Phase 3: ZMQ Publishers (3 seconds + startup time)

**What happens:**
- Launches Kraken tick publisher (port 5558)
- Launches Kraken depth publisher (port 5560)
- Launches Kraken orders publisher (port 5561)
- Launches OANDA tick publisher (port 5562)
- Launches Betfair stream publisher (port 5564)

Each publisher:
- Connects to data source
- Binds to ZMQ PUB socket
- Starts publishing on configured topics

**Verification:**
```bash
# Check publisher processes
ps aux | grep publisher

# List active ports
netstat -an | grep LISTEN | grep 555[0-9]
```

### Phase 4: Grafana Dashboards (5 seconds)

**What happens:**
- Waits for Grafana to be fully ready
- Creates InfluxDB datasource
- Provisions 5 dashboards:
  - kraken_tick_stream
  - kraken_depth_stream
  - kraken_orders_stream
  - oanda_tick_stream
  - betfair_stream

**Verification:**
```bash
# Check dashboards in Grafana UI
curl http://localhost:3000/api/dashboards/db -u admin:admin123
```

### Phase 5: Message Validation (15 seconds)

**What happens:**
- Monitors each ZMQ topic for incoming messages
- Connects as subscriber to each publisher
- Counts messages received in 10-second windows
- Validates data in InfluxDB
- Verifies measurements have data points

**Expected Output:**
```
✓ kraken_tick: 150 messages, rate: 15.0 msg/sec
✓ kraken_depth: 80 messages, rate: 8.0 msg/sec
✓ oanda_tick: 100 messages, rate: 10.0 msg/sec
✓ ALL TOPICS STREAMING SUCCESSFULLY
✓ INFLUXDB DATA INGESTION SUCCESSFUL
```

---

## Configuration

### integration_config.json

Central configuration file for the entire system.

#### Docker Services

```json
{
  "docker": {
    "compose_file": "./docker-compose.yml",
    "services": {
      "influxdb": {
        "container_name": "nbpy-influxdb",
        "port": 8086,
        "health_check_url": "http://localhost:8086/ping"
      },
      "grafana": {
        "container_name": "nbpy-grafana",
        "port": 3000,
        "admin_user": "admin",
        "admin_password": "admin123"
      }
    }
  }
}
```

#### Retention Policies

```json
{
  "influxdb": {
    "retention_policies": {
      "default": {
        "duration": "30d",
        "replication": 1,
        "shard_duration": "1d",
        "default": true
      },
      "high_frequency": {
        "duration": "7d",
        "replication": 1,
        "shard_duration": "6h"
      },
      "long_term": {
        "duration": "365d",
        "replication": 1,
        "shard_duration": "30d"
      }
    }
  }
}
```

#### Publishers Configuration

```json
{
  "publishers": [
    {
      "name": "kraken_tick",
      "module": "nbpy.zmq.publishers.kraken_tick",
      "class": "KrakenTickPublisher",
      "port": 5558,
      "topic": "kraken_tick",
      "enabled": true
    }
  ]
}
```

#### Subscribers Configuration

```json
{
  "subscribers": [
    {
      "name": "kraken_influxdb_tick",
      "module": "nbpy.zmq.subscribers.kraken_influxdb_tick",
      "class": "KrakenTickToInfluxDBSubscriber",
      "port": 5578,
      "subscribe_to": "kraken_tick",
      "publisher_host": "localhost",
      "publisher_port": 5558,
      "influxdb_measurement": "kraken_tick",
      "enabled": true
    }
  ]
}
```

#### Measurements

```json
{
  "influxdb": {
    "measurements": {
      "kraken_tick": {
        "fields": ["bid", "ask", "last_trade_price", "volume", "vwap"],
        "tags": ["pair", "exchange"]
      },
      "kraken_depth": {
        "fields": ["bid_price", "bid_size", "ask_price", "ask_size"],
        "tags": ["pair", "level", "exchange"]
      }
    }
  }
}
```

---

## Monitoring and Health Checks

### System Status

```bash
./integrated_startup.sh status
```

Shows:
- Docker container status
- ZMQ publisher processes (running/stopped)
- ZMQ subscriber processes (running/stopped)
- Port assignments
- Uptime information

### Message Validation

Validate the complete message streaming pipeline:

```bash
# Full validation (ZMQ + InfluxDB)
./integrated_startup.sh validate

# Standalone validation
python3 db/message_validator.py --config integration_config.json full

# ZMQ only
python3 db/message_validator.py --config integration_config.json zmq

# InfluxDB only
python3 db/message_validator.py --config integration_config.json influxdb
```

### Health Metrics

Monitor health metrics:

```bash
# Get InfluxDB stats
python3 db/retention_policy.py --config integration_config.json stats

# View specific measurement data count
python3 -c "
from db.retention_policy import RetentionPolicyManager
manager = RetentionPolicyManager()
manager.connect()
count = manager.get_data_points_count('kraken_tick')
print(f'kraken_tick points: {count}')
"
```

### Log Files

Access detailed logs:

```bash
# Startup log
tail -f logs/integrated_startup.log

# Service manager log
tail -f logs/service_manager.log

# Message validator log
tail -f logs/message_validator.log

# Retention policy log
tail -f logs/retention_policy.log

# Grafana setup log
tail -f logs/grafana_setup.log

# Individual service logs
tail -f logs/kraken_tick.log
tail -f logs/kraken_depth.log
tail -f logs/oanda_tick.log
```

### Docker Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs -f influxdb
docker-compose logs -f grafana

# Follow new logs
docker-compose logs -f
```

---

## Troubleshooting

### Issue: Docker Services Won't Start

**Symptoms:**
```
Error response from daemon: Conflict. The container name "/nbpy-influxdb" is already in use
```

**Solution:**
```bash
# Remove existing containers
docker-compose down -v

# Check for orphaned containers
docker ps -a
docker rm <container_id>

# Retry startup
./integrated_startup.sh start
```

### Issue: Ports Already In Use

**Symptoms:**
```
bind: address already in use
```

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :8086
sudo lsof -i :3000
sudo lsof -i :5558

# Kill the process
kill -9 <pid>

# Or modify ports in docker-compose.yml and integration_config.json
```

### Issue: No Messages in InfluxDB

**Symptoms:**
```
Validation: ✗ kraken_tick: 0 points
```

**Debugging:**
```bash
# Check if publishers are running
ps aux | grep publisher

# Monitor a topic directly
python3 db/message_validator.py zmq --duration 20

# Check subscriber logs
tail -f logs/kraken_influxdb_tick.log

# Verify InfluxDB connectivity
curl -u zmq:zmq http://localhost:8086/query?db=tick&q=SHOW%20MEASUREMENTS

# Check if data is being written
python3 db/retention_policy.py list
```

### Issue: Grafana Dashboards Not Showing Data

**Symptoms:**
```
Grafana dashboards empty or gray
```

**Solution:**
1. Verify InfluxDB datasource is configured
2. Check that measurements have data:
   ```bash
   python3 db/retention_policy.py stats
   ```
3. Verify dashboard queries are correct
4. Refresh Grafana browser page
5. Check datasource health in Grafana UI → Configuration → Data Sources

### Issue: Graceful Shutdown Timeout

**Symptoms:**
```
Services not stopping within 30 seconds
```

**Solution:**
```bash
# Force stop with shorter timeout
./integrated_startup.sh stop

# Or manually kill services
pkill -f "kraken_tick"
pkill -f "kraken_depth"
docker-compose down --force-remove-volumes
```

### Issue: Memory Usage Too High

**Symptoms:**
```
System becoming slow, high memory usage
```

**Solution:**
```bash
# Check memory usage
free -h
docker stats

# Reduce retention policy duration
python3 db/retention_policy.py cleanup

# Or configure smaller shard durations in integration_config.json
```

---

## API Reference

### Integrated Startup Script

```bash
./integrated_startup.sh <command>
```

#### Commands

| Command | Description |
|---------|-------------|
| `start` | Start entire system with all phases |
| `stop` | Gracefully stop all services |
| `restart` | Stop then start the system |
| `status` | Show status of all components |
| `validate` | Validate message streaming |

#### Environment Variables

```bash
# Override Python executable
PYTHON=/path/to/python ./integrated_startup.sh start

# Override config path
CONFIG_PATH=./custom_config.json ./integrated_startup.sh start

# View logs
SCRIPT_DIR=/home/textolytics/nbpy tail -f ./logs/integrated_startup.log
```

### Service Manager API

```bash
python3 db/service_manager.py <command> [options]
```

#### Commands

```bash
# Start all publishers and subscribers
python3 db/service_manager.py --config integration_config.json start

# Stop all services
python3 db/service_manager.py --config integration_config.json stop

# Get service status
python3 db/service_manager.py --config integration_config.json status

# Restart services
python3 db/service_manager.py --config integration_config.json restart

# Monitor and auto-restart failed services
python3 db/service_manager.py --config integration_config.json monitor
```

### Retention Policy Manager API

```bash
python3 db/retention_policy.py <command> [options]
```

#### Commands

```bash
# Create/configure retention policies
python3 db/retention_policy.py --config integration_config.json create

# List retention policies
python3 db/retention_policy.py --config integration_config.json list

# Show database statistics
python3 db/retention_policy.py --config integration_config.json stats

# Cleanup old data
python3 db/retention_policy.py --config integration_config.json cleanup
```

### Message Validator API

```bash
python3 db/message_validator.py <command> [options]
```

#### Commands

```bash
# Validate ZMQ message streaming
python3 db/message_validator.py --config integration_config.json \
  --duration 20 zmq

# Validate InfluxDB data ingestion
python3 db/message_validator.py --config integration_config.json influxdb

# Full validation (ZMQ + InfluxDB)
python3 db/message_validator.py --config integration_config.json \
  --duration 15 full
```

### Grafana Setup API

```bash
python3 db/grafana_setup.py <command> [options]
```

#### Commands

```bash
# Full Grafana setup
python3 db/grafana_setup.py --config integration_config.json setup

# Only setup datasource
python3 db/grafana_setup.py --config integration_config.json datasource

# Only create dashboards
python3 db/grafana_setup.py --config integration_config.json dashboards
```

---

## Performance Tuning

### Optimize InfluxDB Performance

```bash
# Increase batch size
export INFLUXDB_BATCH_SIZE=5000

# Increase write consistency
export INFLUXDB_WRITE_CONSISTENCY=quorum

# Adjust retention policy shard duration
# Smaller shards = faster queries, more CPU
# Larger shards = slower queries, less CPU
```

### Optimize ZMQ Performance

```bash
# Increase high water mark (message buffer)
# In publisher: socket.setsockopt(zmq.SNDHWM, 10000)
# In subscriber: socket.setsockopt(zmq.RCVHWM, 10000)
```

### Monitor System Performance

```bash
# Real-time system monitoring
watch -n 1 'docker stats --no-stream'

# Check disk usage
df -h /var/lib/docker/volumes/

# Monitor network traffic
nethogs
```

---

## Advanced Usage

### Custom Publishers

Extend the system with custom publishers:

```python
from nbpy.zmq import BasePublisher, PortConfig

class CustomPublisher(BasePublisher):
    def __init__(self):
        port_config = PortConfig(
            port=5570,
            service_name='custom_publisher',
            service_type='PUB',
            description='Custom data publisher'
        )
        super().__init__(port_config)
    
    def run(self, interval=1.0):
        self.running = True
        while self.running:
            # Publish custom data
            self.publish_msgpack('custom_topic', {'data': 'value'})
            time.sleep(interval)

if __name__ == '__main__':
    publisher = CustomPublisher()
    publisher.run()
```

### Custom Subscribers

Create custom subscribers:

```python
from nbpy.zmq import BaseSubscriber

class CustomSubscriber(BaseSubscriber):
    def process_message(self, topic, message):
        # Process incoming message
        print(f"Received on {topic}: {message}")
        
        # Forward to InfluxDB or other storage
        self.influxdb_service.write_points([...])

if __name__ == '__main__':
    subscriber = CustomSubscriber()
    subscriber.run()
```

### Backup and Recovery

```bash
# Backup InfluxDB data
docker exec nbpy-influxdb influxd backup -database tick /tmp/backup

# Restore InfluxDB data
docker exec nbpy-influxdb influxd restore -database tick /tmp/backup

# Export data as JSON
curl -u zmq:zmq "http://localhost:8086/query?db=tick&q=SELECT%20*%20FROM%20kraken_tick" \
  > kraken_tick_backup.json
```

---

## Support and Documentation

- **Configuration**: See `integration_config.json` for detailed options
- **Logs**: Check `logs/` directory for detailed debugging information
- **Code**: See `db/` and `nbpy/zmq/` for implementation details
- **Docker**: Run `docker-compose logs` for container diagnostics

---

## License

NBPY ZMQ Microservices - Part of textolytics/nbpy project

