# InfluxDB Service Integration Guide

## Overview

The nbpy database module provides a complete framework for capturing market data from ZMQ publishers and persisting it to InfluxDB. This guide shows how to integrate the database services with your nbpy ZMQ infrastructure.

## Architecture

```
ZMQ Publishers          ZMQ-InfluxDB Bridge        InfluxDB Server
─────────────────       ───────────────────        ───────────────
pub_oanda_tick.py       OandaTickBridge            [tick database]
pub_kraken_tick.py  →   KrakenTickBridge      →    [depth database]
pub_kraken_depth.py     GenericZMQBridge           [ohlc database]
                                                   [sentiment db]
```

## Setup Steps

### Step 1: Install Dependencies

```bash
pip install influxdb zmq
```

### Step 2: Configure InfluxDB

Create a `.env` file in the nbpy root directory:

```bash
cat > /home/textolytics/nbpy/.env << 'EOF'
# InfluxDB Configuration
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8086
INFLUXDB_USER=zmq
INFLUXDB_PASSWORD=zmq
INFLUXDB_DB=tick
INFLUXDB_SSL=false
INFLUXDB_VERIFY_SSL=true
INFLUXDB_TIMEOUT=10
INFLUXDB_BATCH_SIZE=500
INFLUXDB_CONSISTENCY=one
INFLUXDB_RETENTION=autogen
EOF
```

### Step 3: Verify InfluxDB Connection

```bash
python3 -c "from nbpy.db import InfluxDBService; s = InfluxDBService(); print('Connected!' if s.client else 'Failed')"
```

## Integration Scenarios

### Scenario 1: Direct Integration with Existing Subscriber Scripts

Enhance existing subscriber scripts to use the new database module:

**Before:**
```python
from influxdb import InfluxDBClient
client = InfluxDBClient('localhost', 8086, 'zmq', 'zmq', 'tick')
# ... manual data formatting ...
client.write_points(tick_json)
```

**After:**
```python
from nbpy.db import InfluxDBService, parse_kraken_tick_message

service = InfluxDBService()

while True:
    response = socket.recv_string()
    topic, messagedata = response.split()
    
    tick = parse_kraken_tick_message(messagedata)
    service.write_point(tick)
    service.flush()
```

### Scenario 2: Using ZMQ Bridges

For a cleaner architecture, use the ZMQ bridges:

#### Kraken Tick Service

**File:** `/home/textolytics/nbpy/db/services/kraken_tick_service.py`

```python
#!/usr/bin/env python3

import sys
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db import create_kraken_bridge

def main():
    """Run Kraken tick to InfluxDB service"""
    bridge = create_kraken_bridge(zmq_port=5558)
    
    def signal_handler(sig, frame):
        print("\nShutdown signal received")
        bridge.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    bridge.run(blocking=True)

if __name__ == "__main__":
    main()
```

Run it:
```bash
python3 /home/textolytics/nbpy/db/services/kraken_tick_service.py
```

#### OANDA Tick Service

**File:** `/home/textolytics/nbpy/db/services/oanda_tick_service.py`

```python
#!/usr/bin/env python3

import sys
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db import create_oanda_bridge

def main():
    """Run OANDA tick to InfluxDB service"""
    bridge = create_oanda_bridge(zmq_port=5556)
    
    def signal_handler(sig, frame):
        print("\nShutdown signal received")
        bridge.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    bridge.run(blocking=True)

if __name__ == "__main__":
    main()
```

### Scenario 3: Aggregated Service Management

Update the service manager script to include database services:

**File:** `/home/textolytics/nbpy/python/scripts/zmq/nbpy_zmq_service.sh`

Add database services to the `SERVICES` array:

```bash
declare -a SERVICES=(
  # ... existing publishers and subscribers ...
  "nbpy_zmq_influxdb_kraken_tick:Kraken Tick to InfluxDB:${PYTHON_BIN} /home/textolytics/nbpy/db/services/kraken_tick_service.py"
  "nbpy_zmq_influxdb_oanda_tick:OANDA Tick to InfluxDB:${PYTHON_BIN} /home/textolytics/nbpy/db/services/oanda_tick_service.py"
)
```

## Python API Usage

### Basic Usage Pattern

```python
from nbpy.db import InfluxDBService, TickData

# Create service
service = InfluxDBService()

try:
    # Create data
    tick = TickData(
        instrument="EURUSD",
        bid=1.0856,
        ask=1.0858,
        base_ccy="EUR",
        term_ccy="USD"
    )
    
    # Write to service (buffered)
    service.write_point(tick)
    
    # Optionally flush immediately
    if should_flush:
        service.flush(force=True)
        
finally:
    service.close()
```

### Batch Operations

```python
from nbpy.db import InfluxDBService, TickData

service = InfluxDBService()

# Collect data
ticks = []
for i in range(100):
    ticks.append(TickData(
        instrument="EURUSD",
        bid=1.0856 + i * 0.0001,
        ask=1.0858 + i * 0.0001
    ))

# Write all at once
service.write_points(ticks)

# Automatic flush when buffer exceeds batch_size
service.close()
```

### Configuration Management

```python
from nbpy.db import ConfigManager, InfluxDBConfig, InfluxDBService

# Get global config manager
config_mgr = ConfigManager()

# Get base configuration (from env vars or files)
base_config = config_mgr.get_base_config()

# Get service-specific configuration
tick_config = config_mgr.get_service_config('tick')

# Create service with merged config
config = InfluxDBConfig(**tick_config)
service = InfluxDBService(config)
```

## Data Flow Examples

### Kraken Publisher → InfluxDB

```
pub_kraken_tick.py
    ↓
    ZMQ Publisher (port 5558)
    ↓
KrakenTickBridge (subscribes to "kraken_tick")
    ↓
    Parses message: instrument, ask_price, bid_price, ...
    ↓
    Creates TickData object
    ↓
InfluxDBService (batches and writes)
    ↓
    InfluxDB "tick" database
```

### OANDA Publisher → InfluxDB

```
pub_oanda_tick.py
    ↓
    ZMQ Publisher (port 5556)
    ↓
OandaTickBridge (subscribes to "oanda_tick")
    ↓
    Parses message: instrument, timestamp, bid, ask
    ↓
    Creates TickData object
    ↓
InfluxDBService (batches and writes)
    ↓
    InfluxDB "tick" database
```

## Monitoring and Maintenance

### Health Check

```python
from nbpy.db import InfluxDBService

service = InfluxDBService()

stats = service.get_stats()
print(f"Connected: {stats['connected']}")
print(f"Buffered points: {stats['buffered_points']}")
print(f"Total writes: {stats['total_writes']}")
print(f"Total errors: {stats['total_errors']}")
```

### Querying Stored Data

```python
from nbpy.db import InfluxDBService

service = InfluxDBService()

# Get latest EURUSD tick
latest = service.get_latest_tick("EURUSD")
print(f"Latest EURUSD: bid={latest['bid']}, ask={latest['ask']}")

# Get last 24 hours of OHLC data
ohlc = service.get_ohlc("EURUSD", hours=24)
print(f"Got {len(ohlc)} candles")

# Custom query
results = service.query(
    'SELECT * FROM "tick" WHERE "instrument"=\'EURUSD\' AND time > now() - 1h'
)
```

### Error Recovery

```python
from nbpy.db import InfluxDBService
import time

service = InfluxDBService()

# Automatic reconnection on write failure
for attempt in range(3):
    try:
        service.write_point(tick)
        break
    except Exception as e:
        print(f"Write failed: {e}")
        if service.reconnect():
            print("Reconnected, retrying...")
            time.sleep(1)
        else:
            print("Failed to reconnect")
            break
```

## Production Deployment

### Service Definition (systemd)

**File:** `/etc/systemd/system/nbpy-kraken-influxdb.service`

```ini
[Unit]
Description=nbpy Kraken to InfluxDB Service
After=network.target influxdb.service

[Service]
Type=simple
User=textolytics
WorkingDirectory=/home/textolytics/nbpy
Environment="PYTHONPATH=/home/textolytics/nbpy"
ExecStart=/home/textolytics/nbpy/bin/python3 /home/textolytics/nbpy/db/services/kraken_tick_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nbpy-kraken-influxdb
sudo systemctl start nbpy-kraken-influxdb
```

### Logging

```bash
# View logs
sudo journalctl -u nbpy-kraken-influxdb -f

# Log to file
sudo journalctl -u nbpy-kraken-influxdb > /var/log/nbpy-kraken-influxdb.log
```

## Troubleshooting

### Connection Refused

```python
from nbpy.db import InfluxDBService

service = InfluxDBService()

if not service.client:
    print("✗ Cannot connect to InfluxDB")
    print(f"  Host: localhost")
    print(f"  Port: 8086")
    # Check if InfluxDB is running and accessible
```

### Data Not Appearing

```python
# Check database exists
service = InfluxDBService()
databases = service.client.get_list_database()
print([db['name'] for db in databases])

# Check if data was actually written
results = service.query('SELECT * FROM "tick" LIMIT 1')
print(results)
```

### Performance Issues

- Increase `batch_size` in configuration
- Run writes in background thread
- Monitor memory usage of InfluxDB process

## Example Implementation

See `examples.py` for complete working examples:

```bash
python3 /home/textolytics/nbpy/db/examples.py
```

## Next Steps

1. **Test the connection**: Run the health check script
2. **Deploy services**: Use the service manager to start database services
3. **Monitor data flow**: Check InfluxDB for incoming data
4. **Set up retention policies**: Configure automatic data cleanup
5. **Create dashboards**: Use Grafana to visualize market data

## References

- [InfluxDB Python Client Documentation](https://influxdb-client.readthedocs.io/)
- [ZMQ Documentation](https://zeromq.org/get-started/)
- [nbpy Service Manager](../python/scripts/zmq/nbpy_zmq_service.sh)
