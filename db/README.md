# nbpy Database Services

Comprehensive database integration module for the nbpy project, providing real-time time-series data storage from ZMQ publishers to InfluxDB.

## Overview

The `db` module provides:

- **InfluxDB Service**: Core connection management and data persistence
- **Data Models**: Type-safe dataclasses for different data types (Tick, Depth, OHLC, Sentiment)
- **Configuration Management**: Environment variable, file-based, and service-specific configurations
- **ZMQ Integration**: Direct bridges from ZMQ publishers to InfluxDB storage
- **Error Handling**: Automatic reconnection and retry logic
- **Batch Processing**: Configurable batch writes for performance

## Installation

```bash
pip install influxdb zmq
```

## Quick Start

### Basic InfluxDB Service

```python
from nbpy.db import InfluxDBService, TickData

# Create service with default configuration
service = InfluxDBService()

# Create tick data
tick = TickData(
    instrument="EURUSD",
    bid=1.0856,
    ask=1.0858,
    base_ccy="EUR",
    term_ccy="USD"
)

# Write data point
service.write_point(tick)

# Flush to InfluxDB
service.flush(force=True)

# Close connection
service.close()
```

### Using Context Manager

```python
from nbpy.db import InfluxDBService, TickData

with InfluxDBService() as service:
    tick = TickData(instrument="EURUSD", bid=1.0856, ask=1.0858)
    service.write_point(tick)
    service.flush(force=True)
    # Automatically closes on exit
```

### ZMQ to InfluxDB Bridge

```python
from nbpy.db import create_kraken_bridge

# Create and run Kraken tick bridge
bridge = create_kraken_bridge(zmq_port=5558)
bridge.run(blocking=True)  # Runs in current thread

# Or run in background
bridge.run(blocking=False)
# ... do other work ...
bridge.stop()
```

## Configuration

### Environment Variables

```bash
export INFLUXDB_HOST=192.168.0.33
export INFLUXDB_PORT=8086
export INFLUXDB_USER=zmq
export INFLUXDB_PASSWORD=zmq
export INFLUXDB_DB=tick
export INFLUXDB_BATCH_SIZE=500
```

### Configuration File (.env)

Create `.env` file:

```
INFLUXDB_HOST=192.168.0.33
INFLUXDB_PORT=8086
INFLUXDB_USER=zmq
INFLUXDB_PASSWORD=zmq
INFLUXDB_DB=tick
INFLUXDB_BATCH_SIZE=500
```

### Programmatic Configuration

```python
from nbpy.db import InfluxDBService, InfluxDBConfig

config = InfluxDBConfig(
    host="192.168.0.33",
    port=8086,
    username="zmq",
    password="zmq",
    database="tick",
    batch_size=500
)

service = InfluxDBService(config)
```

## Data Models

### TickData

Market tick data with bid/ask prices:

```python
from nbpy.db import TickData

tick = TickData(
    instrument="EURUSD",
    bid=1.0856,
    ask=1.0858,
    base_ccy="EUR",
    term_ccy="USD",
    volume=1000000,
    vwap=1.0857
)
```

### DepthData

Order book depth information:

```python
from nbpy.db import DepthData

depth = DepthData(
    instrument="EURUSD",
    bid_prices=[1.0856, 1.0855, 1.0854],
    bid_volumes=[1000000, 500000, 250000],
    ask_prices=[1.0858, 1.0859, 1.0860],
    ask_volumes=[1000000, 500000, 250000],
    base_ccy="EUR",
    term_ccy="USD"
)
```

### OHLCData

Candlestick data:

```python
from nbpy.db import OHLCData

ohlc = OHLCData(
    instrument="EURUSD",
    open=1.0850,
    high=1.0860,
    low=1.0845,
    close=1.0858,
    volume=1000000,
    trades=5000
)
```

### SentimentData

Market sentiment information:

```python
from nbpy.db import SentimentData

sentiment = SentimentData(
    source="twitter",
    instrument="EURUSD",
    sentiment_score=0.75,
    text="EUR is strengthening",
    location="global",
    language="en"
)
```

## ZMQ Bridges

### Built-in Bridges

#### Kraken Tick Bridge

```python
from nbpy.db import create_kraken_bridge

bridge = create_kraken_bridge(zmq_port=5558)
bridge.run(blocking=True)
```

Subscribes to `kraken_tick` topic and stores tick data.

#### OANDA Tick Bridge

```python
from nbpy.db import create_oanda_bridge

bridge = create_oanda_bridge(zmq_port=5556)
bridge.run(blocking=True)
```

Subscribes to `oanda_tick` topic and stores tick data.

### Custom Bridges

```python
from nbpy.db import create_generic_bridge, TickData

def custom_parser(message):
    """Parse custom message format"""
    fields = message.split(',')
    return TickData(
        instrument=fields[0],
        bid=float(fields[1]),
        ask=float(fields[2])
    )

bridge = create_generic_bridge(
    zmq_port=5555,
    topic_filter="custom_tick",
    parser_func=custom_parser,
    service_name="custom_bridge"
)

bridge.run(blocking=True)
```

## Advanced Usage

### Batch Writing

```python
from nbpy.db import InfluxDBService, TickData

service = InfluxDBService()

# Write multiple points (buffered)
ticks = [
    TickData(instrument="EURUSD", bid=1.0856, ask=1.0858),
    TickData(instrument="GBPUSD", bid=1.2650, ask=1.2652),
    TickData(instrument="USDJPY", bid=110.45, ask=110.47),
]

service.write_points(ticks)

# Manually flush
service.flush(force=True)
```

### Querying Data

```python
from nbpy.db import InfluxDBService

service = InfluxDBService()

# Get latest tick
latest = service.get_latest_tick("EURUSD")
print(latest)

# Get OHLC data
ohlc_data = service.get_ohlc("EURUSD", hours=24)
for candle in ohlc_data:
    print(candle)

# Custom query
results = service.query(
    'SELECT * FROM "tick" WHERE "instrument"=\'EURUSD\' LIMIT 10'
)
```

### Service Statistics

```python
service = InfluxDBService()
stats = service.get_stats()

print(f"Connected: {stats['connected']}")
print(f"Total writes: {stats['total_writes']}")
print(f"Total errors: {stats['total_errors']}")
```

## Integration with nbpy ZMQ Services

The database module integrates seamlessly with the nbpy ZMQ services defined in `python/scripts/zmq/`:

- `pub_oanda_tick.py` → `OandaTickBridge`
- `pub_kraken_tick.py` → `KrakenTickBridge`
- `pub_kraken_EURUSD_depth.py` → `GenericZMQBridge` (custom parser)

### Example: Running with Service Manager

```bash
# Start the aggregated service manager
/home/textolytics/nbpy/python/scripts/zmq/nbpy_zmq_service.sh install

# Start all services
/home/textolytics/nbpy/python/scripts/zmq/nbpy_zmq_service.sh start all
```

Data from these services is automatically persisted to InfluxDB using the bridges.

## Error Handling

The module includes automatic error handling:

```python
from nbpy.db import InfluxDBService

service = InfluxDBService()

try:
    # Write data
    service.write_point(tick)
    service.flush()
except Exception as e:
    print(f"Error: {e}")
finally:
    service.close()
```

### Automatic Reconnection

If the InfluxDB connection is lost, the service will automatically attempt to reconnect:

```python
# Reconnect manually
if not service.client:
    service.reconnect()
```

## Performance Tuning

### Batch Size

```python
from nbpy.db import InfluxDBConfig, InfluxDBService

config = InfluxDBConfig(batch_size=1000)  # Larger batches
service = InfluxDBService(config)
```

### Time Precision

The service uses millisecond precision by default. For different precision:

```python
# Modify in influxdb_service.py write_points call
self.client.write_points(
    self.batch_buffer,
    time_precision='s'  # seconds instead of ms
)
```

## Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

from nbpy.db import InfluxDBService
service = InfluxDBService()  # Now with debug output
```

## Testing

```python
from nbpy.db import InfluxDBService, TickData

# Test connection
service = InfluxDBService()
if service.client:
    print("✓ Connected to InfluxDB")
else:
    print("✗ Failed to connect")

# Test write
tick = TickData(instrument="TEST", bid=1.0, ask=1.0)
if service.write_point(tick):
    print("✓ Data written")
    service.flush(force=True)

service.close()
```

## File Structure

```
db/
├── __init__.py                  # Package initialization
├── influxdb_service.py          # Core InfluxDB service
├── config.py                    # Configuration management
├── zmq_influxdb_bridge.py       # ZMQ integration
├── config.example.json          # Example configuration
├── .env.example                 # Example environment file
└── README.md                    # This file
```

## Environment Configuration

See [config.py](config.py) for detailed configuration options.

## Troubleshooting

### Connection Issues

```python
from nbpy.db import InfluxDBService

service = InfluxDBService()

# Check if connected
if not service.client:
    print("Not connected to InfluxDB")
    # Check host, port, credentials
```

### Performance Issues

- Increase `batch_size` for fewer write operations
- Adjust `timeout` for slow networks
- Monitor `write_count` and `error_count` in statistics

### Data Not Appearing

- Check InfluxDB database exists
- Verify credentials
- Check timestamp precision (should be milliseconds)
- Use `service.query()` to check raw data

## License

Part of the nbpy project

## Contributing

Contributions welcome! Submit pull requests or issues.
