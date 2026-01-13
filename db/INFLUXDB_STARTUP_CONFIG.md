# InfluxDB 2.x Default Startup Configuration

This document describes the default Docker configuration for InfluxDB 2.7 with GUI accessible on port 8086.

## Quick Start

### Starting the Service

```bash
cd /home/textolytics/nbpy/db
docker-compose up -d influxdb
```

### Accessing the GUI

- **URL**: http://localhost:8086
- **Default Credentials**:
  - Username: `admin`
  - Password: `adminpassword`

## Configuration Details

### Docker Compose Setup

The `docker-compose.yml` file includes:

- **Image**: `influxdb:2.7-alpine` - Official InfluxDB 2.7 image
- **Container Name**: `nbpy_influxdb`
- **Port Mapping**: `8086:8086` (HTTP API and Web UI)
- **Volumes**:
  - `influxdb_data`: Persistent data storage
  - `influxdb_config`: Configuration storage
- **Health Check**: Monitors `/health` endpoint every 30 seconds
- **Network**: `nbpy_network` for communication with other services (e.g., Grafana)

### Initial Setup Environment Variables

```env
INFLUXDB_INIT_MODE=setup              # Enable initial setup mode
INFLUXDB_INIT_USERNAME=admin          # Admin username
INFLUXDB_INIT_PASSWORD=adminpassword  # Admin password
INFLUXDB_INIT_ORG=nbpy               # Organization name
INFLUXDB_INIT_BUCKET=tick            # Default bucket for time-series data
INFLUXDB_INIT_RETENTION=30d          # Data retention period
INFLUXDB_INIT_ADMIN_TOKEN=zmq-admin-token-secret  # Admin token
INFLUXDB_UI_ENABLED=true             # Enable the web UI
```

### Dockerfile

The `Dockerfile` uses `influxdb:2.7-alpine` as the base image and:
- Configures the same environment variables for initialization
- Exposes ports 8086 (HTTP API/UI) and 8088 (RPC for backups)
- Implements health checks
- Uses the official entrypoint script

## Common Operations

### View Logs

```bash
docker logs nbpy_influxdb
```

### Stop the Service

```bash
docker-compose down
```

### Access the Container Shell

```bash
docker exec -it nbpy_influxdb bash
```

### Verify Service Health

```bash
curl -s http://localhost:8086/health
```

## Notes

- **First Run**: The initial setup is automatic on first container start
- **Data Persistence**: All data is stored in the `influxdb_data` volume
- **Port 8088**: Used for backup/restore operations via RPC
- **Network**: Connected to `nbpy_network` for integration with Grafana and other services

## Troubleshooting

If the container fails to start:

1. Check logs: `docker logs nbpy_influxdb`
2. Verify port 8086 is not in use: `lsof -i :8086`
3. Ensure Docker is running: `docker ps`
4. Check disk space for persistent volumes

## Credentials Management

**Important**: Change the default password after first login:

1. Access the UI at http://localhost:8086
2. Log in with `admin`/`adminpassword`
3. Navigate to Settings → Users
4. Update the admin password

For production, consider using environment variables or secrets management.
