# nbpy_zmq Project Index

## Project Location
```
/home/textolytics/nbpy/nbpy_project/
```

## Directory Structure

```
nbpy_project/
├── nbpy_zmq/                          # Main package (importable module)
│   ├── __init__.py                    # Package initialization
│   ├── publishers/                    # Publisher implementations
│   │   └── __init__.py
│   ├── subscribers/                   # Subscriber implementations  
│   │   └── __init__.py
│   ├── forwarders/                    # Message forwarders/brokers
│   │   └── __init__.py
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       ├── config.py                  # ZMQConfig - centralized settings
│       └── message_bus.py             # MessageBus - ZMQ abstraction
├── tests/                             # Test suite
│   └── test_core.py                   # Unit tests for core functionality
├── examples_publisher.py              # Example: Mock publisher
├── example_subscriber.py              # Example: Mock subscriber
├── setup.py                           # Package configuration
├── requirements.txt                   # Dependencies
├── README.md                          # Package documentation
├── DEVELOPMENT.md                     # Development guide
└── .gitignore                         # Git ignore rules
```

## File Descriptions

### Core Package (`nbpy_zmq/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Exports ZMQConfig and MessageBus |
| `publishers/__init__.py` | Publisher module namespace |
| `subscribers/__init__.py` | Subscriber module namespace |
| `forwarders/__init__.py` | Forwarder module namespace |
| `utils/config.py` | ZMQConfig dataclass for centralized config |
| `utils/message_bus.py` | MessageBus class - ZMQ pub/sub wrapper |

### Configuration & Setup

| File | Purpose |
|------|---------|
| `setup.py` | setuptools configuration for pip install |
| `requirements.txt` | Pip requirements with optional dev extras |
| `.gitignore` | Git ignore patterns |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Package overview and quick start |
| `DEVELOPMENT.md` | Development setup, testing, troubleshooting |

### Examples & Tests

| File | Purpose |
|------|---------|
| `examples_publisher.py` | Example mock publisher (publishes dummy ticks) |
| `example_subscriber.py` | Example mock subscriber (listens to ticks) |
| `tests/test_core.py` | Unit tests for ZMQConfig and MessageBus |

---

## Quick Reference

### Import Core Classes

```python
from nbpy_zmq.utils import ZMQConfig, MessageBus
```

### ZMQConfig

Central configuration for:
- ZMQ host/ports (default: localhost:5559-5560)
- InfluxDB connection (default: 192.168.0.33:8086)
- Kraken/Oanda API endpoints
- Message batch sizes and precision
- Default topic names

**Location**: `nbpy_zmq/utils/config.py`

**Methods**:
- `get_zmq_url(port, host)` — Generate ZMQ URL
- `get_influxdb_url()` — Generate InfluxDB URL

### MessageBus

High-level abstraction for ZMQ pub/sub:
- `create_publisher(port, host)` — Create PUB socket
- `create_subscriber(topics, port, host)` — Create SUB socket
- `send_message(topic, data)` — Publish message
- `receive_message()` → (topic, data) — Receive message
- `close()` — Clean shutdown

**Location**: `nbpy_zmq/utils/message_bus.py`

---

## Installation

### 1. Activate Virtual Environment
```bash
source /home/textolytics/nbpy/nbpy/bin/activate
```

Or use directly:
```bash
/home/textolytics/nbpy/nbpy/bin/python
```

### 2. Install Package
```bash
cd /home/textolytics/nbpy/nbpy_project
pip install -e .
```

### 3. Install Dev Dependencies (Optional)
```bash
pip install -e ".[dev]"
```

---

## Running Examples

### Terminal 1 - Start Publisher
```bash
cd /home/textolytics/nbpy/nbpy_project
/home/textolytics/nbpy/nbpy/bin/python examples_publisher.py
```

Output:
```
Publishing Kraken EURUSD ticks...
Publisher bound to tcp://localhost:5559
Published: {'instrument': 'EUR_USD', 'bid': 1.082, 'ask': 1.0825}
...
```

### Terminal 2 - Start Subscriber
```bash
cd /home/textolytics/nbpy/nbpy_project
/home/textolytics/nbpy/nbpy/bin/python example_subscriber.py
```

Output:
```
Listening for Kraken EURUSD ticks...
Subscriber connected to tcp://localhost:5559, topics: ['kr_eurusd_tick']
[kr_eurusd_tick] instrument=EUR_USD, bid=1.082, ask=1.0825
...
```

---

## Testing

### Run All Tests
```bash
cd /home/textolytics/nbpy/nbpy_project
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/ -v
```

### Run with Coverage
```bash
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/ --cov=nbpy_zmq --cov-report=html
```

### Run Single Test
```bash
/home/textolytics/nbpy/nbpy/bin/python -m pytest tests/test_core.py::test_zmq_config_defaults -v
```

---

## Dependencies

### Core
- **pyzmq** (27.1.0) — ZMQ message bus
- **influxdb** (5.3.2) — InfluxDB client
- **requests** (2.32.5) — HTTP library
- **ccs** (0.1.11) — Kraken API wrapper
- **vaderSentiment** (3.3.2) — Sentiment analysis
- **psycopg2-binary** (2.9.11) — PostgreSQL client

### Development (optional)
- **pytest** — Testing framework
- **pytest-cov** — Coverage reports
- **black** — Code formatter
- **flake8** — Linter
- **mypy** — Type checker

---

## Integration with Existing Scripts

The existing ZMQ scripts are located in:
```
/home/textolytics/nbpy/python/scripts/zmq/
```

Can be refactored to use the new package:

**Before**:
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://localhost:5559")
socket.send_string("topic message")
```

**After**:
```python
from nbpy_zmq.utils import ZMQConfig, MessageBus

config = ZMQConfig()
bus = MessageBus(config)
pub = bus.create_publisher()
bus.send_message("topic", "message")
```

---

## Environment Variables (Optional)

Create `.env` in project root:
```
INFLUXDB_HOST=192.168.0.33
INFLUXDB_PORT=8086
INFLUXDB_USER=zmq
INFLUXDB_PASSWORD=zmq
KRAKEN_API_KEY=your_key
OANDA_API_KEY=your_key
```

Load with:
```python
from dotenv import load_dotenv
import os
load_dotenv()
host = os.getenv("INFLUXDB_HOST")
```

---

## Key Design Patterns

### Message Format
```
topic\x01instrument\x01bid\x01ask\x01...
```

### Publisher Pattern
1. Create config
2. Initialize MessageBus
3. Create publisher socket
4. Send formatted messages

### Subscriber Pattern
1. Create config
2. Initialize MessageBus
3. Subscribe to topics
4. Receive and parse messages
5. Write to database

### Database Pattern
- InfluxDB for time-series metrics
- PostgreSQL for structured queries
- Batch writes with `time_precision='ms'`

---

## Troubleshooting

### Port Already in Use
```bash
lsof -i :5559
kill -9 <PID>
```

### Import Error
```bash
pip install -e .
```

### Database Connection
```bash
/home/textolytics/nbpy/nbpy/bin/python -c \
  "from influxdb import InfluxDBClient; print(InfluxDBClient('192.168.0.33', 8086).ping())"
```

### ZMQ Connection Refused
Check publisher is running on correct port and that subscriber connects to same port.

---

## Related Documentation

- [README.md](README.md) — Package overview
- [DEVELOPMENT.md](DEVELOPMENT.md) — Development setup guide
- [../SETUP_SUMMARY.md](../SETUP_SUMMARY.md) — Project creation summary
- [../.github/copilot-instructions.md](../.github/copilot-instructions.md) — AI agent instructions

---

**Status**: ✓ Ready for development and integration  
**Python Version**: 3.13.5  
**Installation Status**: ✓ Installed in virtual environment  
**Last Updated**: 2025-12-30
