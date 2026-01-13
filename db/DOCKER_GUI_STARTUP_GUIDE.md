# Docker Services Configuration - Default GUI Startup

This document describes the complete Docker setup for running InfluxDB and Grafana with GUI access.

## Quick Start

### Start All Services

```bash
cd /home/textolytics/nbpy/db
sudo docker-compose up -d
```

Or use the provided startup script:

```bash
./start-all-services.sh
```

### Access the GUIs

**InfluxDB 2.7:**
- **URL**: http://localhost:8086
- **Username**: admin
- **Password**: adminpassword
- **Purpose**: Time-series database management and querying

**Grafana 12.3:**
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: adminpassword
- **Purpose**: Dashboard creation and visualization

## Configuration Overview

### Docker Compose Structure

The `docker-compose.yml` file defines two main services:

#### 1. InfluxDB Service
- **Image**: `influxdb:2.7-alpine`
- **Container**: `nbpy_influxdb`
- **Port**: 8086 (HTTP API and Web UI)
- **Data Volumes**:
  - `influxdb_data`: Persistent time-series data
  - `influxdb_config`: Configuration storage
- **Health Check**: Every 30 seconds via `/health` endpoint
- **Restart Policy**: unless-stopped

**Environment Configuration:**
```yaml
INFLUXDB_INIT_MODE: setup                          # Enable initial setup
INFLUXDB_INIT_USERNAME: admin                      # Admin user
INFLUXDB_INIT_PASSWORD: adminpassword              # Admin password
INFLUXDB_INIT_ORG: nbpy                           # Organization
INFLUXDB_INIT_BUCKET: tick                        # Default bucket
INFLUXDB_INIT_RETENTION: 30d                      # Data retention
INFLUXDB_INIT_ADMIN_TOKEN: zmq-admin-token-secret # Admin token
INFLUXDB_UI_ENABLED: "true"                       # Enable UI
INFLUXDB_REPORTING_DISABLED: "false"              # Reporting enabled
```

#### 2. Grafana Service
- **Image**: `grafana/grafana:latest`
- **Container**: `nbpy_grafana`
- **Port**: 3000 (Web UI)
- **Data Volume**: `grafana_data` (persistent dashboards and settings)
- **Config Volume**: `./grafana/provisioning` (read-only provisioning)
- **Health Check**: Every 30 seconds via `/api/health` endpoint
- **Restart Policy**: unless-stopped
- **Depends On**: InfluxDB (will start after InfluxDB)

**Environment Configuration:**
```yaml
GF_SECURITY_ADMIN_USER: admin                      # Admin username
GF_SECURITY_ADMIN_PASSWORD: adminpassword          # Admin password
GF_INSTALL_PLUGINS: grafana-piechart-panel        # Installed plugins
GF_USERS_ALLOW_SIGN_UP: "false"                   # Disable sign-up
GF_SERVER_ROOT_URL: http://localhost:3000         # Server URL
GF_SECURITY_COOKIE_SECURE: "false"                # Cookie settings
```

### Network Configuration

Both services are connected to a custom Docker network `nbpy_network` (bridge driver), allowing:
- Direct communication between InfluxDB and Grafana using service names
- Isolation from other Docker networks
- Easy addition of other services

### Volume Management

**Named Volumes:**
- `influxdb_data`: Stores InfluxDB time-series data
- `influxdb_config`: Stores InfluxDB configuration
- `grafana_data`: Stores Grafana dashboards and settings

**Bind Mounts:**
- `./grafana/provisioning`: Grafana provisioning configurations (read-only)

## Common Operations

### View Service Status

```bash
sudo docker-compose ps
```

### View Logs

```bash
# InfluxDB logs
sudo docker logs -f nbpy_influxdb

# Grafana logs
sudo docker logs -f nbpy_grafana

# Both services
sudo docker-compose logs -f
```

### Access Container Shell

```bash
# InfluxDB
sudo docker exec -it nbpy_influxdb bash

# Grafana
sudo docker exec -it nbpy_grafana bash
```

### Restart Services

```bash
# Restart all services
sudo docker-compose restart

# Restart specific service
sudo docker-compose restart influxdb
sudo docker-compose restart grafana
```

### Stop Services

```bash
# Stop all services (keeps containers)
sudo docker-compose stop

# Remove all containers and networks
sudo docker-compose down

# Remove everything including volumes (WARNING: deletes data)
sudo docker-compose down -v
```

### Health Checks

```bash
# InfluxDB health
curl -s http://localhost:8086/health

# Grafana health
curl -s http://localhost:3000/api/health

# Combined check
echo "InfluxDB:" && curl -s http://localhost:8086/health | grep -o '"status":"[^"]*"'
echo "Grafana:" && curl -s http://localhost:3000/api/health | grep -o '"database":"[^"]*"'
```

## Initial Setup

### First Time Running

1. **Start containers:**
   ```bash
   sudo docker-compose up -d
   ```

2. **Wait for services to be ready** (~10-15 seconds)

3. **Access InfluxDB:**
   - Navigate to http://localhost:8086
   - Log in with: `admin` / `adminpassword`
   - Initial setup will be pre-configured with organization "nbpy" and bucket "tick"

4. **Access Grafana:**
   - Navigate to http://localhost:3000
   - Log in with: `admin` / `adminpassword`
   - Configure InfluxDB as data source (use container name "influxdb" as hostname)

### Connecting Grafana to InfluxDB

1. Log in to Grafana (http://localhost:3000)
2. Go to **Configuration** → **Data Sources**
3. Click **Add Data Source**
4. Select **InfluxDB**
5. Configure:
   - **Name**: InfluxDB
   - **URL**: http://influxdb:8086
   - **Organization**: nbpy
   - **Token**: zmq-admin-token-secret
   - **Default Bucket**: tick
6. Click **Save & Test**

## Troubleshooting

### Port Already in Use

If you get "address already in use" error:

```bash
# Find process using port 8086
sudo netstat -tlnp | grep 8086

# Kill the process
sudo kill <PID>

# Try starting again
sudo docker-compose up -d
```

### Container Won't Start

Check logs:
```bash
sudo docker-compose logs influxdb
sudo docker-compose logs grafana
```

### Services Not Communicating

Ensure both containers are on the same network:
```bash
sudo docker network inspect db_nbpy_network
```

### Reset to Fresh State

```bash
# Stop and remove everything
sudo docker-compose down -v

# Clean up dangling images
sudo docker image prune -f

# Start fresh
sudo docker-compose up -d
```

## Advanced Configuration

### Custom Credentials

Edit `docker-compose.yml` to change default credentials:

**For InfluxDB:**
```yaml
INFLUXDB_INIT_USERNAME: your_username
INFLUXDB_INIT_PASSWORD: your_password
```

**For Grafana:**
```yaml
GF_SECURITY_ADMIN_USER: your_username
GF_SECURITY_ADMIN_PASSWORD: your_password
```

Then restart:
```bash
sudo docker-compose down && sudo docker-compose up -d
```

### Persistent Data

All data is persisted in Docker volumes. To back up:

```bash
# Backup InfluxDB data
sudo docker run --rm -v influxdb_data:/data -v $(pwd):/backup ubuntu tar czf /backup/influxdb_data.tar.gz -C /data .

# Backup Grafana data
sudo docker run --rm -v grafana_data:/data -v $(pwd):/backup ubuntu tar czf /backup/grafana_data.tar.gz -C /data .
```

### Performance Tuning

Modify resource limits in `docker-compose.yml`:

```yaml
services:
  influxdb:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Security Considerations

⚠️ **Important**: The default credentials should be changed in production:

1. After first login, change passwords in both InfluxDB and Grafana UIs
2. Consider using environment files (`.env`) for credentials
3. Use firewall rules to restrict access to ports 8086 and 3000
4. Enable HTTPS for production deployments

## Additional Resources

- [InfluxDB 2.x Documentation](https://docs.influxdata.com/influxdb/latest/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
