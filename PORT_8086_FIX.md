# Fix: "Address Already in Use" Error on Port 8086

## Problem
When running `./startup_guide.sh`, Docker fails with:
```
Error response from daemon: driver failed programming external connectivity...
Error starting userland proxy: listen tcp4 0.0.0.0:8086: bind: address already in use
```

## Root Cause
InfluxDB is installed as a **system service** (not just Docker) and is running on port 8086, conflicting with the Docker container attempt.

## Solution

### Quick Fix (Recommended for Docker Deployment)

**Stop the system InfluxDB service:**
```bash
sudo systemctl stop influxdb
```

**Disable it from auto-starting:**
```bash
sudo systemctl disable influxdb
```

**Verify port 8086 is now free:**
```bash
sudo netstat -tulpn | grep 8086
# Should return NO results if successful
```

### Then Start the System
```bash
cd /home/textolytics/nbpy
sudo ./startup_guide.sh
```

---

## Alternative Solutions

### Option A: Use Different Port (Keep System InfluxDB)
If you want to keep the system InfluxDB running, modify the Docker port:

1. **Edit `docker-compose.yml`:**
```yaml
services:
  influxdb:
    ports:
      - "8087:8086"  # Change from 8086 to 8087
```

2. **Edit `integration_config.json`:**
```json
{
  "influxdb": {
    "port": 8087  // Change from 8086 to 8087
  }
}
```

3. **Start the system:**
```bash
sudo ./startup_guide.sh
```

### Option B: Remove System InfluxDB Entirely
If you don't need the system InfluxDB:

```bash
# Stop the service
sudo systemctl stop influxdb

# Remove the package
sudo apt-get remove influxdb

# Remove configuration
sudo apt-get purge influxdb
```

### Option C: Use Docker Exclusively
Keep system InfluxDB stopped but don't disable it:

```bash
# Stop it for now
sudo systemctl stop influxdb

# Start your Docker-based system
sudo ./startup_guide.sh

# If system reboots, you'll need to stop it again
# To make it permanent, disable auto-start:
sudo systemctl disable influxdb
```

---

## Quick Verification

**Check what's using port 8086:**
```bash
sudo netstat -tulpn | grep 8086
```

**Expected output after fix:**
```
(No results - port is free)
```

**Check system InfluxDB service status:**
```bash
sudo systemctl status influxdb
```

**Expected output after fix:**
```
● influxdb.service - InfluxDB is an open-source...
   Loaded: loaded (...; disabled; vendor preset: enabled)
   Active: inactive (dead)
```

---

## Recommended Setup

For the NBPY integrated system, **Option A (Stop System Service)** is recommended because:

✅ Docker containers are isolated and manageable  
✅ Easy to restart the system  
✅ Proper cleanup on shutdown  
✅ No port conflicts  
✅ Can be reversed: `sudo systemctl start influxdb` if needed  

---

## Troubleshooting

**If port still shows as in use after stopping:**
```bash
# Kill any remaining processes
sudo lsof -i :8086
# Kill the PID shown
sudo kill -9 <PID>
```

**If Docker still fails:**
```bash
# Restart Docker daemon
sudo systemctl restart docker

# Remove all containers
sudo docker system prune -f

# Try again
sudo ./startup_guide.sh
```

**If you need both (system and Docker InfluxDB):**
Use different ports and manage them separately:
- System InfluxDB: port 8086
- Docker InfluxDB: port 8087 (via config changes above)

---

## Prevention

To avoid this issue in future startups:

1. **Add to your startup script:**
```bash
#!/bin/bash
# Kill system InfluxDB before Docker startup
sudo systemctl stop influxdb 2>/dev/null || true
sleep 2
./startup_guide.sh
```

2. **Or add to `integrated_startup.sh`** (if permanent Docker migration):
```bash
# Ensure no conflicting services
echo "Stopping system InfluxDB..."
sudo systemctl stop influxdb 2>/dev/null || true
sleep 2
```

---

## Status After Fix

✅ Port 8086 is available for Docker InfluxDB  
✅ Docker can bind to the port successfully  
✅ `startup_guide.sh` runs without connection errors  
✅ Grafana and other services can initialize properly  

**Ready to start:** `sudo ./startup_guide.sh`
