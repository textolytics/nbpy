# nbpy Project Setup Summary

## Python Project Structure Created

A complete Python project structure for **nbpy_zmq** has been created at:
```
/home/textolytics/nbpy/nbpy_project/
```

## What Was Generated

### 1. **Package Structure** (`nbpy_zmq/`)
```
nbpy_zmq/
├── __init__.py              # Package initialization
├── publishers/              # Publisher implementations (Kraken, Oanda, Twitter)
├── subscribers/             # Subscriber implementations (InfluxDB, PostgreSQL)
├── forwarders/              # Message broker/forwarder implementations
└── utils/
    ├── config.py           # Centralized ZMQConfig class
    └── message_bus.py      # MessageBus abstraction for ZMQ pub/sub
```

### 2. **Core Dependencies Installed**
- ✓ `pyzmq>=27.0.0` — ZMQ message bus
- ✓ `influxdb>=5.3.1` — InfluxDB time-series storage
- ✓ `requests>=2.28.0` — HTTP client for APIs
- ✓ `ccs>=0.1.11` — Kraken API wrapper
- ✓ `vaderSentiment>=3.3.2` — Sentiment analysis
- ✓ `psycopg2-binary>=2.9.0` — PostgreSQL client

### 3. **Key Files**

| File | Purpose |
|------|---------|
| `setup.py` | Package installation configuration |
| `requirements.txt` | Dependency list |
| `README.md` | Project documentation |
| `DEVELOPMENT.md` | Setup and development guide |
| `nbpy_zmq/utils/config.py` | ZMQ and service configuration |
| `nbpy_zmq/utils/message_bus.py` | High-level ZMQ abstraction |
| `examples_publisher.py` | Example publisher script |
| `example_subscriber.py` | Example subscriber script |
| `tests/test_core.py` | Unit tests |

## Python Virtual Environment

The project uses the existing venv:
```
/home/textolytics/nbpy/nbpy/bin/python
```

**Version**: Python 3.13.5

**To activate**:
```bash
source /home/textolytics/nbpy/nbpy/bin/activate
```

## Quick Start

### 1. Install in Development Mode
```bash
cd /home/textolytics/nbpy/nbpy_project
pip install -e .
```

### 2. Run Publisher Example
```bash
/home/textolytics/nbpy/nbpy/bin/python examples_publisher.py
```

### 3. Run Subscriber Example (in another terminal)
```bash
/home/textolytics/nbpy/nbpy/bin/python example_subscriber.py
```

## Core Classes

### ZMQConfig
Centralized configuration for all ZMQ, InfluxDB, and API settings:
```python
from nbpy_zmq.utils import ZMQConfig

config = ZMQConfig(
    host="localhost",
    pub_port=5559,
    influxdb_host="192.168.0.33"
)
```

### MessageBus
High-level abstraction for ZMQ pub/sub operations:
```python
from nbpy_zmq.utils import MessageBus

bus = MessageBus(config)
pub = bus.create_publisher()
sub = bus.create_subscriber(topics=["kr_eurusd_tick"])
bus.send_message("topic", "data")
topic, data = bus.receive_message()
bus.close()
```

## Message Format

Messages use ZMQ topic-based pub/sub with tab-separated values:
```
topic\x01instrument\x01bid\x01ask\x01...
```

Example:
```python
message_data = "\x01".join(["EUR_USD", "1.0820", "1.0825"])
bus.send_message("kr_eurusd_tick", message_data)
```

## Integration with Existing Scripts

The project provides a foundation for wrapping existing scripts:

**Existing publishers** in `/home/textolytics/nbpy/python/scripts/zmq/`:
- `pub_kraken_EURUSD.py`
- `pub_kraken_depth.py`
- `pub_oanda_tick.py`
- etc.

**Can be refactored** to use the new package structure:
```python
from nbpy_zmq.utils import ZMQConfig, MessageBus

config = ZMQConfig()
bus = MessageBus(config)
pub = bus.create_publisher()
# ... fetch data and publish
```

## Testing

Run unit tests:
```bash
cd /home/textolytics/nbpy/nbpy_project
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/ -v
```

## Next Steps

1. **Migrate existing publishers**: Refactor scripts in `python/scripts/zmq/pub_*.py` to use `nbpy_zmq.publishers`
2. **Migrate existing subscribers**: Refactor scripts in `python/scripts/zmq/sub_*.py` to use `nbpy_zmq.subscribers`
3. **Add integration tests**: Connect to real InfluxDB/PostgreSQL in `tests/`
4. **Create CLI tools**: Build command-line interfaces for running publishers/subscribers
5. **Document database schemas**: Add schema documentation for InfluxDB and PostgreSQL

## Verification

✓ Package installed successfully
✓ All imports working
✓ ZMQConfig loads with correct defaults
✓ MessageBus initializes correctly
✓ Dependencies resolved

---

**Project Location**: `/home/textolytics/nbpy/nbpy_project/`  
**Python Executable**: `/home/textolytics/nbpy/nbpy/bin/python`  
**Installation Status**: ✓ Ready for development
