# Docker Configuration Summary

## Overview
The db module has been configured to run with Docker containers for InfluxDB and Grafana services using the following credentials:
- **Username**: zmq
- **Password**: y61327061
- **Container Hostname**: influxdb (for InfluxDB service)
- **Default Host**: influxdb (Docker service name)

## Updated Files

### 1. influxdb_service.py
**Changes:**
- Default host changed from `localhost` to `influxdb` (Docker service name)
- Default password changed from `zmq` to `y61327061`
- Build lib version updated similarly

### 2. .env.example
**Changes:**
- Host: `influxdb` (Docker container hostname)
- User: `zmq`
- Password: `y61327061`

### 3. docker-compose.yml (Recreated)
**Key Features:**
- **InfluxDB Service:**
  - Image: `influxdb:1.8-alpine`
  - Container name: `nbpy_influxdb`
  - Hostname: `influxdb`
  - Port: 8086
  - Authentication enabled with zmq/y61327061
  - Health check includes credentials

- **Grafana Service:**
  - Image: `grafana/grafana:latest`
  - Container name: `nbpy_grafana`
  - Port: 3000
  - Admin user: zmq
  - Admin password: y61327061
  - Sign-up disabled
  - Depends on InfluxDB service

### 4. init-databases.sh
**Changes:**
- Added INFLUX_USER and INFLUX_PASSWORD environment variables
- All influx CLI commands now include authentication credentials
- Default host: `influxdb`
- Default credentials: zmq/y61327061
- Creates multiple databases: tick, ohlc, depth, orders, sentiment, _internal

### 5. Documentation Updates
- README.md: Updated configuration examples
- build/lib/db/config.py: Updated example templates with Docker defaults

## Running Docker Containers

### Start Services
```bash
cd /home/textolytics/nbpy/db
docker-compose up -d
```

### Access Services
- **InfluxDB HTTP API**: `http://localhost:8086`
- **Grafana Dashboard**: `http://localhost:3000`

### Authentication
- **InfluxDB CLI**:
  ```bash
  influx -host influxdb -username zmq -password y61327061
  ```

- **InfluxDB HTTP API**:
  ```bash
  curl -u zmq:y61327061 http://localhost:8086/ping
  ```

- **Grafana**: Login with zmq/y61327061

## Environment Variables
All services can be configured via environment variables:
- `INFLUXDB_HOST=influxdb` (default in Docker)
- `INFLUXDB_PORT=8086`
- `INFLUXDB_USER=zmq`
- `INFLUXDB_PASSWORD=y61327061`
- `INFLUXDB_DB=tick`
- `INFLUXDB_ADMIN_USER=zmq`
- `INFLUXDB_ADMIN_PASSWORD=y61327061`

## Python Configuration
Default configuration in Python code:
```python
from nbpy.db import InfluxDBConfig

config = InfluxDBConfig(
    host='influxdb',        # Docker service name
    port=8086,
    username='zmq',
    password='y61327061',
    database='tick'
)
```

When running within Docker network, use `influxdb` as hostname.
When running locally, use `localhost` or `127.0.0.1`.
