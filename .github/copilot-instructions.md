# Copilot Instructions for nbpy

## Project Overview

**nbpy** is a market data ETL and analytics workspace for forex and cryptocurrency trading. It ingests tick data from Oanda (forex) and Kraken (crypto), publishes via ZMQ message bus, and stores in InfluxDB/PostgreSQL for time-series analysis and sentiment studies.

### Core Stack
- **Data Sources**: Oanda API, Kraken API, Twitter/RSS feeds
- **Message Bus**: ZMQ (PUB/SUB pattern on localhost ports 5559-5560)
- **Databases**: InfluxDB (metrics), PostgreSQL (structured data)
- **Languages**: Python (orchestration), C/C++ (utilities via CMake)

## Architecture & Data Flow

### ZMQ Message Bus Pattern (Critical)

The workspace uses **ZMQ topic-based pub/sub** for decoupling data producers from consumers:

1. **Publishers** (in `python/scripts/zmq/pub_*.py`): Fetch market data and publish to ZMQ
   - Example: `pub_kraken_EURUSD.py` → publishes on topic `kr_eurusd_tick`
   - Example: `pub_oanda_tick.py` → publishes on topic `oanda_tick`

2. **Subscribers** (in `python/scripts/zmq/sub_*.py`): Listen on topics and persist to backends
   - `sub_kraken_EURUSD_tick_influxdb.py` → writes to InfluxDB
   - `sub_kraken_EURUSD_tick_pgsql.py` → writes to PostgreSQL

3. **Forwarder** (in `zmq/forwarder_server.py`): Acts as message distributor/repeater

**Key insight**: Message format is `topic messagedata` where messagedata contains tab-separated (`\x01`) values. Example from `pub_kraken_depth.py`:
```python
instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, ... = messagedata.split('\x01')
```

### Synthetic Basket Generation

Cross-rate arbitrage logic runs in `pub_kraken_depth.py`:
- Subscribes to `kr_eurusd_tick` (primary pair)
- Fetches order books via Kraken API for hedge pairs (e.g., EUR/USD and USD/JPY)
- Publishes derived depth data on `kr_depth` topic
- Pattern: Convert 3-letter currency code (last 3 chars) to identify hedge pairs

### Data Persistence

- **InfluxDB**: Time-series measurements (ticks, synthetic spreads) with tags (instrument, t0/t1) and fields (bid, ask, spread)
- **PostgreSQL**: Structured queries via continuous views (from PipelineDB era); see `db/pipeline_oanda.sql`
- **Typical write pattern**: Batch writes with `batch_size=500` and `time_precision='ms'`

## Critical Developer Workflows

### Running ZMQ Services

1. **Start a publisher** (publishes to ZMQ):
   ```bash
   python3 python/scripts/zmq/pub_kraken_EURUSD.py
   ```

2. **Start a subscriber** (reads from ZMQ, writes to InfluxDB):
   ```bash
   python3 python/scripts/zmq/sub_kraken_EURUSD_tick_influxdb.py
   ```

Both services run as daemons; output is logged. Multi-service orchestration via shell scripts in `python/scripts/zmq/sh/`.

### Building C/C++ Components

```bash
cd c/
cmake . -B cmake-build-debug
cd cmake-build-debug && make
```

The main executable (`C`) is built from `c/main.cpp`. Complex utilities may use external libraries; check `CMakeLists.txt` for linkage.

### Database Access

- **InfluxDB**: Connect to `192.168.0.33:8086` (user: `zmq`, password: `zmq`, db: `tick`)
- **PostgreSQL**: Continuous views referenced in `db/pipeline_oanda.sql`
- **Telegraf**: Configuration in `conf/telegraf.conf` for data collection

## Project-Specific Conventions

### Naming Patterns

- **Forex pairs**: 3-letter base + underscore + 3-letter quote (e.g., `EUR_USD`, `USD_JPY`)
- **Kraken pairs**: Prefixed with `kr_` or `KR_` (e.g., `kr_eurusd_tick`, `KR_EURUSD`)
- **Topics**: Lowercase snake_case; plural forms rare (e.g., `kr_depth`, not `kr_depths`)

### File Organization

- **Publishers**: `pub_*.py` (source data producers)
- **Subscribers**: `sub_*.py` (data consumers)
- **Utilities**: `c/`, `python/scripts/` (reusable functions)
- **Shell runners**: `*.sh` files (orchestration; often contain hardcoded paths)

### JSON Message Format

Tick messages (most common):
```json
{
  "timestmp": "2025-08-29T12:34:56.123Z",
  "instrument": "USD_JPY",
  "bid": 151.2345,
  "ask": 151.2348,
  "source": "oanda"
}
```

Synthetic basket snapshot:
```json
{
  "snapshot_ts": "2025-08-29T12:35:00Z",
  "basket": "EURUSD_synthetic",
  "components": [
    {"instrument": "EUR_USD", "weight": 0.6, "price": 1.0823}
  ],
  "value": 65.4321
}
```

## Integration Points & Dependencies

### External APIs

- **Oanda**: REST API at `stream-fxpractice.oanda.com` (practice) or `stream-fxtrade.oanda.com` (live)
- **Kraken**: Python wrapper in `python/scripts/crypto/kraken/krakenex/`; methods like `kraken.public.getOrderBook(instrument, depth)`

### Sentiment Analysis (Twitter/RSS)

- **VaderSentiment** library: Used in `python/scripts/twitter_influx_sentiment_location.py`
- **Output**: Geo-tagged sentiment scores (-1 to +1) written to InfluxDB with lat/lon tags

### Common Import Paths

```python
import zmq              # Message bus
from influxdb import InfluxDBClient  # Metrics storage
import ccs              # Kraken API wrapper (local)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # NLP
```

## Troubleshooting & Notes

- **ZMQ connection refused**: Verify publisher is running on correct port (5559 default); check `python/scripts/zmq/pub_*.py`
- **InfluxDB write failures**: Ensure `batch_size` and `time_precision='ms'` match schema expectations
- **Currency pair mismatches**: Confirm 3-letter base/quote codes match Kraken/Oanda API responses
- **Shell script paths**: Many `.sh` files contain hardcoded user paths (`/home/sdreep/`, `/home/betsy/`) — update for your environment
- **Python 2 vs 3**: Workspace mixed (shebang lines vary); prefer Python 3 for new work

## Key Files to Reference

- [c/CMakeLists.txt](c/CMakeLists.txt) — Build configuration
- [python/scripts/zmq/pub_kraken_depth.py](python/scripts/zmq/pub_kraken_depth.py) — Synthetic basket logic
- [python/scripts/zmq/sub_kraken_EURUSD_tick_influxdb.py](python/scripts/zmq/sub_kraken_EURUSD_tick_influxdb.py) — InfluxDB writer pattern
- [db/pipeline_oanda.sql](db/pipeline_oanda.sql) — SQL view patterns
- [python/scripts/twitter_influx_sentiment_location.py](python/scripts/twitter_influx_sentiment_location.py) — Sentiment pipeline
