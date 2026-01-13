# NBPY ZMQ Services - Startup Guide

## Quick Start

### 1. Start All Services (One Command)

```bash
cd /home/textolytics/nbpy
./startup.sh start
```

This will:
- ✅ Start InfluxDB container
- ✅ Start Grafana container
- ✅ Start configured ZMQ publishers
- ✅ Start configured ZMQ subscribers
- ✅ Open dashboards in your browser

### 2. Check Service Status

```bash
./startup.sh status
```

Shows:
- Docker container status
- Python service status
- Port availability
- Overall health

### 3. View Logs

```bash
# Follow all service logs in real-time
./startup.sh logs

# View recent summary
./startup.sh logsummary

# Follow Docker logs only
./startup.sh docker-logs
```

### 4. Stop All Services

```bash
./startup.sh stop
```

### 5. Restart Services

```bash
./startup.sh restart
```

---

## Web Dashboards

Once services are running, access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **InfluxDB UI** | http://localhost:8083 | admin / admin123 |
| **InfluxDB API** | http://localhost:8086 | zmq / zmq |

### Manually Open Dashboards

```bash
./startup.sh open
```

---

## Configuration

### View Current Configuration

```bash
./startup.sh config
```

Shows:
- Installation paths
- Docker service endpoints
- ZMQ ports and topics
- Configured publishers and subscribers
- Credentials

### Customize Publishers/Subscribers

Edit `startup.sh` and modify these sections:

```bash
ZMQ_PUBLISHERS=(
    "kraken-tick"
    "kraken-depth"
    "oanda-tick"
    # Add more...
)

ZMQ_SUBSCRIBERS=(
    "kraken-influxdb-tick"
    "oanda-influxdb-tick"
    # Add more...
)
```

Then restart:
```bash
./startup.sh restart
```

---

## Troubleshooting

### Services Won't Start

```bash
# Verify Python environment
./startup.sh config

# Test imports
/home/textolytics/nbpy/nbpy/bin/python -c "from nbpy.zmq import BasePublisher"

# Check ports are available
netstat -tln | grep -E "5558|5559|8086|3000"
```

### Docker Services Not Starting

```bash
# Check Docker installation
docker --version
docker-compose --version

# View Docker logs
./startup.sh docker-logs

# Manually check containers
docker ps -a
docker logs nbpy-influxdb
docker logs nbpy-grafana
```

### Port Already in Use

```bash
# Find what's using port 8086 (InfluxDB)
lsof -i :8086

# Kill it or use different port
kill -9 <PID>
# Or edit docker-compose.yml to use different port
```

### Python Services Not Running

```bash
# Check logs
tail -f logs/pub_*.log
tail -f logs/sub_*.log

# Verify nbpy installation
/home/textolytics/nbpy/nbpy/bin/pip list | grep nbpy

# Reinstall if needed
/home/textolytics/nbpy/nbpy/bin/pip install -e .
```

### No Data in InfluxDB

```bash
# Check if publishers are running
./startup.sh status

# Verify connectivity
nc -zv localhost 5558

# Check InfluxDB directly
curl http://localhost:8086/query?q=SHOW%20DATABASES

# View recent logs
./startup.sh logsummary
```

---

## Manual Service Management

### Start Individual Services

```bash
# Start Docker services only
docker-compose -f docker-compose.yml up -d

# Start specific publisher
/home/textolytics/nbpy/nbpy/bin/python -m nbpy.zmq.publishers.kraken_tick

# Start specific subscriber
/home/textolytics/nbpy/nbpy/bin/python -m nbpy.zmq.subscribers.kraken_influxdb_tick
```

### Stop Individual Services

```bash
# Stop Docker
docker-compose -f docker-compose.yml down

# Kill Python process
kill -9 <PID>
```

### Monitor Data Flow

```bash
# Subscribe to Kraken tick messages
python -c "
import zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5558')
socket.setsockopt_string(zmq.SUBSCRIBE, 'kraken_tick')
while True:
    print(socket.recv())
"

# Query InfluxDB
curl "http://localhost:8086/query?db=tick&q=SELECT%20*%20FROM%20kraken_tick%20LIMIT%205"
```

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              NBPY ZMQ Architecture                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Publishers (Data Sources)                                 │
│  ├─ kraken-tick (port 5558)                               │
│  ├─ kraken-depth (port 5560)                              │
│  ├─ kraken-orders (port 5561)                             │
│  ├─ oanda-tick (port 5562)                                │
│  └─ betfair-stream (port 5564)                            │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │         ZMQ PUB/SUB Network (localhost)           │      │
│  │      MessagePack Binary Serialization             │      │
│  └──────────────────────────────────────────────────┘      │
│         │                                                   │
│         ▼                                                   │
│  Subscribers (Data Sinks)                                  │
│  ├─ kraken-influxdb-tick                                  │
│  ├─ kraken-influxdb-depth                                 │
│  ├─ oanda-influxdb-tick                                   │
│  ├─ kraken-pgsql-tick                                     │
│  └─ ... (27 total)                                         │
│         │                                                   │
│         ▼                                                   │
│  Storage & Processing                                      │
│  ├─ InfluxDB (time-series) ◄─── docker: localhost:8086    │
│  ├─ PostgreSQL (relational)                               │
│  ├─ Grakn (graph database)                                │
│  └─ Kapacitor (stream processing)                         │
│         │                                                   │
│         ▼                                                   │
│  Visualization                                             │
│  └─ Grafana ◄─── docker: localhost:3000                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Advanced Usage

### Enable Specific Publishers Only

```bash
# Edit startup.sh
ZMQ_PUBLISHERS=(
    "kraken-tick"
    # Comment out others
)

./startup.sh restart
```

### Monitor Specific Service

```bash
# Watch logs for a service
tail -f logs/pub_kraken_tick.log

# Or use journalctl if installed as service
journalctl -u nbpy-pub-kraken-tick -f
```

### Performance Tuning

```bash
# Increase socket buffers for high throughput
# Edit nbpy/zmq/base.py and increase:
# socket.setsockopt(zmq.SNDBUF, 1024*1024*10)  # 10MB

./startup.sh restart
```

### Setup as Systemd Service

Create `/etc/systemd/system/nbpy.service`:

```ini
[Unit]
Description=NBPY ZMQ Microservices
After=network.target

[Service]
Type=simple
User=textolytics
WorkingDirectory=/home/textolytics/nbpy
ExecStart=/home/textolytics/nbpy/startup.sh start
ExecStop=/home/textolytics/nbpy/startup.sh stop
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nbpy
sudo systemctl start nbpy
sudo systemctl status nbpy
```

---

## Documentation

- **Complete Service Reference**: [SERVICES_INDEX.md](nbpy/zmq/SERVICES_INDEX.md)
- **Migration Details**: [MIGRATION_COMPLETE.md](nbpy/zmq/MIGRATION_COMPLETE.md)
- **Technical Report**: [ZMQ_MIGRATION_FINAL_REPORT.md](ZMQ_MIGRATION_FINAL_REPORT.md)
- **Port Registry**: [nbpy/zmq/ports.py](nbpy/zmq/ports.py)
- **Base Classes**: [nbpy/zmq/base.py](nbpy/zmq/base.py)

---

## Support

### Common Commands

```bash
# All services
./startup.sh start              # Start all
./startup.sh stop               # Stop all
./startup.sh restart            # Restart all
./startup.sh status             # Check status
./startup.sh logs               # View logs
./startup.sh config             # Show configuration

# Testing
/home/textolytics/nbpy/nbpy/bin/python nbpy/zmq/validate.py

# Manual import test
/home/textolytics/nbpy/nbpy/bin/python -c "from nbpy.zmq import *; print('OK')"
```

### Quick Health Check

```bash
# All in one
./startup.sh status && echo "✓ All systems operational"
```

---

## Next Steps

1. **Start the services**: `./startup.sh start`
2. **Open Grafana**: http://localhost:3000 (admin/admin123)
3. **Create dashboards**: Configure data sources and visualizations
4. **Monitor data**: Check InfluxDB for incoming data
5. **Fine-tune**: Adjust publishers/subscribers as needed

Enjoy your ZMQ microservices! 🚀
