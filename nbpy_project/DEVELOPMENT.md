# Development Guide for nbpy_zmq

## Setup

### 1. Activate Virtual Environment

```bash
source /home/textolytics/nbpy/nbpy/bin/activate
```

Or use the full Python path:
```bash
/home/textolytics/nbpy/nbpy/bin/python
```

### 2. Install Package in Development Mode

```bash
cd /home/textolytics/nbpy/nbpy_project
pip install -e .
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

## Running Examples

### Start Publisher (in one terminal)

```bash
cd /home/textolytics/nbpy/nbpy_project
python examples_publisher.py
```

Expected output:
```
2025-12-30 10:15:30,123 - __main__ - INFO - Publishing Kraken EURUSD ticks...
2025-12-30 10:15:30,234 - nbpy_zmq.utils.message_bus - INFO - Publisher bound to tcp://localhost:5559
2025-12-30 10:15:30,245 - __main__ - INFO - Published: {'instrument': 'EUR_USD', 'bid': 1.082, 'ask': 1.0825}
```

### Start Subscriber (in another terminal)

```bash
cd /home/textolytics/nbpy/nbpy_project
python example_subscriber.py
```

Expected output:
```
2025-12-30 10:15:32,123 - __main__ - INFO - Listening for Kraken EURUSD ticks...
2025-12-30 10:15:32,234 - nbpy_zmq.utils.message_bus - INFO - Subscriber connected to tcp://localhost:5559, topics: ['kr_eurusd_tick']
2025-12-30 10:15:32,345 - __main__ - INFO - [kr_eurusd_tick] instrument=EUR_USD, bid=1.082, ask=1.0825
```

## Testing

### Run Unit Tests

```bash
cd /home/textolytics/nbpy/nbpy_project
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=nbpy_zmq --cov-report=html
```

## Project Structure

```
nbpy_project/
├── nbpy_zmq/                    # Main package
│   ├── __init__.py             # Package initialization
│   ├── publishers/             # Publisher implementations
│   │   └── __init__.py
│   ├── subscribers/            # Subscriber implementations
│   │   └── __init__.py
│   ├── forwarders/             # Forwarder implementations
│   │   └── __init__.py
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       └── message_bus.py      # ZMQ abstraction layer
├── tests/                      # Test suite
│   └── test_core.py           # Core functionality tests
├── examples_publisher.py       # Publisher example
├── example_subscriber.py       # Subscriber example
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```

## Key Classes

### ZMQConfig

Central configuration management.

```python
from nbpy_zmq.utils import ZMQConfig

config = ZMQConfig(
    host="192.168.0.100",
    pub_port=5559,
    influxdb_host="192.168.0.33"
)
```

### MessageBus

High-level abstraction for ZMQ pub/sub.

```python
from nbpy_zmq.utils import MessageBus

bus = MessageBus(config)

# Publisher
pub_socket = bus.create_publisher()
bus.send_message("topic", "data")

# Subscriber
sub_socket = bus.create_subscriber(topics=["topic"])
topic, data = bus.receive_message()

bus.close()
```

## Common Tasks

### Adding a New Publisher

1. Create file in `nbpy_zmq/publishers/`
2. Inherit from a base class or use `MessageBus` directly
3. Implement data fetching logic
4. Publish to ZMQ topic

### Adding a New Subscriber

1. Create file in `nbpy_zmq/subscribers/`
2. Subscribe to ZMQ topic(s) using `MessageBus`
3. Parse incoming messages
4. Write to database (InfluxDB/PostgreSQL)

### Adding Tests

1. Add test file to `tests/` directory
2. Use pytest framework
3. Run with `pytest tests/`

## Configuration

Edit `nbpy_zmq/utils/config.py` to change:

- ZMQ host/ports
- InfluxDB connection details
- Kraken/Oanda API endpoints
- Message formats and batch sizes

## Database Connections

### InfluxDB

```python
from influxdb import InfluxDBClient

client = InfluxDBClient(
    host='192.168.0.33',
    port=8086,
    username='zmq',
    password='zmq',
    database='tick'
)
```

### PostgreSQL

```python
import psycopg2

conn = psycopg2.connect(
    dbname="nbpy",
    user="postgres",
    password="password",
    host="192.168.0.33"
)
```

## Environment Variables

Optional: Create `.env` file in project root:

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

## Troubleshooting

### ZMQ Port Already in Use

```bash
lsof -i :5559
kill -9 <PID>
```

### Import Errors

Ensure package is installed:
```bash
pip install -e .
```

### Database Connection Failures

Verify credentials and connectivity:
```bash
python -c "from influxdb import InfluxDBClient; print(InfluxDBClient('192.168.0.33', 8086).ping())"
```
