# Project README for nbpy_zmq

# nbpy ZMQ - Market Data ETL Framework

A Python framework for market data ingestion, ETL, and analytics using ZMQ for real-time message distribution.

## Features

- **Multi-source data ingestion**: Oanda (forex), Kraken (crypto), Twitter (sentiment)
- **ZMQ pub/sub message bus**: Decoupled producer/consumer architecture
- **Time-series storage**: InfluxDB integration for metrics, PostgreSQL for structured data
- **Cross-rate arbitrage**: Synthetic basket generation and hedge pair tracking
- **Sentiment analysis**: Twitter stream processing with geolocation tagging

## Project Structure

```
nbpy_project/
├── nbpy_zmq/                 # Main package
│   ├── publishers/           # Data source publishers
│   ├── subscribers/          # Data consumers (DB writers)
│   ├── forwarders/           # Message repeaters
│   └── utils/                # Common utilities
├── tests/                    # Test suite
├── setup.py                  # Package configuration
└── requirements.txt          # Dependencies
```

## Installation

```bash
pip install -e .
# or with dev dependencies:
pip install -e ".[dev]"
```

## Quick Start

### Create a Publisher

```python
from nbpy_zmq.utils import ZMQConfig, MessageBus

config = ZMQConfig()
bus = MessageBus(config)

pub_socket = bus.create_publisher()

# Publish market data
bus.send_message("kr_eurusd_tick", "instrument=EUR_USD\x01bid=1.0823\x01ask=1.0825")
```

### Create a Subscriber

```python
config = ZMQConfig()
bus = MessageBus(config)

sub_socket = bus.create_subscriber(topics=["kr_eurusd_tick"])

while True:
    topic, data = bus.receive_message()
    print(f"Received {topic}: {data}")
```

## Message Format

Messages use topic-based pub/sub with tab-separated (`\x01`) values:

```
topic instrument_t0\x01bid_t0\x01ask_t0\x01instrument_t1\x01bid_t1\x01ask_t1\x01spread
```

## Configuration

Edit `nbpy_zmq/utils/config.py` to customize:
- ZMQ host/ports (default: localhost:5559-5560)
- InfluxDB connection (default: 192.168.0.33:8086)
- API endpoints and credentials
- Message batch sizes and precision

## Key Files

- `publishers/` - Data source adapters
- `subscribers/` - Database writers (InfluxDB, PostgreSQL)
- `forwarders/` - Message brokers and repeaters
- `utils/config.py` - Global configuration
- `utils/message_bus.py` - ZMQ abstraction layer

## External Dependencies

- **Kraken**: Uses `ccs` library for API access
- **Sentiment**: VaderSentiment for text analysis
- **Storage**: InfluxDB and PostgreSQL clients

## License

MIT
