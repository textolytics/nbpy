# nbpy_zmq Quick Reference Card

## Project Location
```
/home/textolytics/nbpy/nbpy_project/
```

## Python Virtual Environment
```bash
# Activate
source /home/textolytics/nbpy/nbpy/bin/activate

# Or use directly
/home/textolytics/nbpy/nbpy/bin/python

# Version: Python 3.13.5
```

---

## Installation

```bash
# First time setup
cd /home/textolytics/nbpy/nbpy_project
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

---

## Core Classes

### ZMQConfig — Centralized Configuration
```python
from nbpy_zmq.utils import ZMQConfig

config = ZMQConfig()
config.host              # localhost
config.pub_port          # 5559
config.influxdb_host     # 192.168.0.33
config.influxdb_port     # 8086

config.get_zmq_url()     # tcp://localhost:5559
config.get_influxdb_url() # http://192.168.0.33:8086
```

### MessageBus — ZMQ Pub/Sub Abstraction
```python
from nbpy_zmq.utils import MessageBus

bus = MessageBus(config)

# Publisher
pub = bus.create_publisher(port=5559)
bus.send_message("topic", "data")

# Subscriber
sub = bus.create_subscriber(topics=["topic"])
topic, data = bus.receive_message()

bus.close()
```

---

## Example: Publisher

```python
from nbpy_zmq.utils import ZMQConfig, MessageBus

config = ZMQConfig()
bus = MessageBus(config)
pub = bus.create_publisher()

# Publish tick data
message = "\x01".join(["EUR_USD", "1.0820", "1.0825"])
bus.send_message("kr_eurusd_tick", message)

bus.close()
```

## Example: Subscriber

```python
from nbpy_zmq.utils import ZMQConfig, MessageBus

config = ZMQConfig()
bus = MessageBus(config)
sub = bus.create_subscriber(topics=["kr_eurusd_tick"])

while True:
    topic, data = bus.receive_message()
    parts = data.split('\x01')
    print(f"{topic}: {parts[0]} bid={parts[1]} ask={parts[2]}")

bus.close()
```

---

## Message Format

ZMQ messages use **topic-separated pub/sub**:
```
topic\x01value1\x01value2\x01value3\x01...
```

### Example: Tick Data
```python
# Create message
message = "\x01".join([
    "EUR_USD",        # instrument
    "1.0820",         # bid
    "1.0825",         # ask
])
# Publish
bus.send_message("kr_eurusd_tick", message)

# Receive and parse
topic, data = bus.receive_message()
instrument, bid, ask = data.split('\x01')
```

---

## Running Examples

### Example 1: Mock Publisher
```bash
/home/textolytics/nbpy/nbpy/bin/python examples_publisher.py
```

### Example 2: Mock Subscriber
```bash
/home/textolytics/nbpy/nbpy/bin/python example_subscriber.py
```

Both scripts can run independently or together (in separate terminals).

---

## Running Tests

```bash
# All tests
cd /home/textolytics/nbpy/nbpy_project
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/ -v

# Specific test
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/test_core.py::test_zmq_config_defaults -v

# With coverage
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/ --cov=nbpy_zmq --cov-report=html
```

---

## Verification

Verify installation:
```bash
/home/textolytics/nbpy/nbpy/bin/python verify_installation.py
```

Expected output: ✓ ALL CHECKS PASSED

---

## Configuration

Edit `/home/textolytics/nbpy/nbpy_project/nbpy_zmq/utils/config.py`:

```python
# ZMQ Settings
host = "localhost"        # ZMQ broker host
pub_port = 5559           # Publisher port
sub_port = 5560           # Subscriber port

# InfluxDB Settings
influxdb_host = "192.168.0.33"
influxdb_port = 8086
influxdb_user = "zmq"
influxdb_password = "zmq"
influxdb_db = "tick"

# Message Settings
message_batch_size = 500
message_time_precision = "ms"

# Default Topics
default_kraken_tick_topic = "kr_eurusd_tick"
default_kraken_depth_topic = "kr_depth"
default_oanda_tick_topic = "oanda_tick"
default_twitter_sentiment_topic = "twitter_sentiment"
```

---

## Dependencies

✓ **pyzmq** (27.1.0) — ZMQ message bus  
✓ **influxdb** (5.3.2) — Time-series database  
✓ **requests** (2.32.5) — HTTP client  
✓ **ccs** (0.1.11) — Kraken API wrapper  
✓ **vaderSentiment** (3.3.2) — Sentiment analysis  
✓ **psycopg2-binary** (2.9.11) — PostgreSQL client  

---

## Package Structure

```
nbpy_zmq/
├── __init__.py              # Package entry point
├── publishers/              # Publisher modules (to be implemented)
├── subscribers/             # Subscriber modules (to be implemented)
├── forwarders/              # Forwarder modules (to be implemented)
└── utils/
    ├── config.py           # Configuration
    └── message_bus.py      # ZMQ abstraction
```

---

## Troubleshooting

### Port already in use?
```bash
lsof -i :5559
kill -9 <PID>
```

### Import error?
```bash
cd /home/textolytics/nbpy/nbpy_project
pip install -e .
```

### Connection refused?
- Ensure publisher is running
- Check port 5559 is accessible
- Verify host is "localhost" or "127.0.0.1"

### InfluxDB connection failed?
```bash
/home/textolytics/nbpy/nbpy/bin/python -c \
  "from influxdb import InfluxDBClient; print(InfluxDBClient('192.168.0.33', 8086).ping())"
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Package overview |
| [INDEX.md](INDEX.md) | Project index and file descriptions |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development guide |
| [verify_installation.py](verify_installation.py) | Verification script |

---

## Next Steps

1. **Review** [INDEX.md](INDEX.md) for detailed project structure
2. **Read** [README.md](README.md) for package documentation
3. **Setup** development environment in [DEVELOPMENT.md](DEVELOPMENT.md)
4. **Run** examples: `examples_publisher.py` and `example_subscriber.py`
5. **Add** publisher/subscriber implementations in `publishers/` and `subscribers/`
6. **Test** with `pytest tests/`

---

**Status**: ✓ Ready  
**Python**: 3.13.5  
**Last Updated**: 2025-12-30
