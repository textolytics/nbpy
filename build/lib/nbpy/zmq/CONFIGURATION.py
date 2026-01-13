"""
Configuration and Best Practices Guide for NBPY ZMQ Microservices

This guide covers:
1. Configuration management for ZMQ services
2. Environment setup
3. Production deployment guidelines
4. Monitoring and logging
5. Performance tuning
"""


def get_configuration_guide():
    return """
================================================================================
  NBPY ZMQ CONFIGURATION AND DEPLOYMENT GUIDE
================================================================================

1. ENVIRONMENT SETUP
====================

1.1 Installation
----------------
# Clone repository
git clone https://github.com/textolytics/nbpy.git
cd nbpy

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install msgpack influxdb pyzmq

1.2 Verify Installation
-----------------------
# Run validation tests
python3 -m nbpy.zmq.validate

# Run setup verification
python3 test_setup.py

1.3 Port Configuration
----------------------
By default, services use the following ports:
  
  PUB Services:
    Kraken Tick          → 5558
    Kraken Depth         → 5559
    Kraken EURUSD Tick   → 5560
    Kraken Orders        → 5561
    OANDA Tick           → 5562
    OANDA Orders         → 5563
    Betfair Stream       → 5564
    Twitter Sentiment    → 5565
  
  SUB Services:
    Kraken InfluxDB Tick → 5578

Ports are centrally managed in:
  nbpy/zmq/ports.py

2. RUNNING SERVICES
===================

2.1 Command-line Interface
--------------------------
# Publisher: Kraken Tick
$ nbpy-pub-kraken-tick

# Publisher: Kraken Depth
$ nbpy-pub-kraken-depth

# Subscriber: To InfluxDB
$ nbpy-sub-kraken-influxdb-tick [zmq_host] [influxdb_host]

2.2 Python API
--------------
# Publisher Example
from nbpy.zmq.publishers.kraken_tick import KrakenTickPublisher

publisher = KrakenTickPublisher()
publisher.run(interval=1.0)  # Publish every 1 second

# Subscriber Example
from nbpy.zmq.subscribers.influxdb_tick import KrakenTickToInfluxDBSubscriber

subscriber = KrakenTickToInfluxDBSubscriber()
subscriber.run()

2.3 Custom Service
------------------
from nbpy.zmq import BasePublisher, PortConfig
import time

class CustomPublisher(BasePublisher):
    def run(self, interval=1.0):
        self.running = True
        while self.running:
            data = self.fetch_data()  # Your logic
            self.publish_json(self.port_config.topic_filter, data)
            time.sleep(interval)

# Define port
port_config = PortConfig(
    port=5600,
    service_name='custom_publisher',
    service_type='PUB',
    description='My custom publisher',
    topic_filter='custom_topic'
)

publisher = CustomPublisher(port_config)
publisher.run()

3. LOGGING CONFIGURATION
========================

3.1 Basic Logging Setup
------------------------
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

3.2 File Logging
----------------
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('nbpy.zmq')
handler = RotatingFileHandler(
    'zmq_services.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

3.3 Log Levels
--------------
DEBUG   - Detailed diagnostic information
INFO    - General informational messages
WARNING - Warning messages for potential issues
ERROR   - Error messages for failures
CRITICAL - Critical failures

Set level in code:
import logging
logging.basicConfig(level=logging.DEBUG)

Or via environment:
export PYTHONLOGLEVEL=DEBUG

4. INFLUXDB CONFIGURATION
=========================

4.1 Connection Settings
-----------------------
Default settings in KrakenTickToInfluxDBSubscriber:

  Host: localhost (change via parameter)
  Port: 8086
  User: zmq
  Password: zmq
  Database: tick

Usage:
subscriber = KrakenTickToInfluxDBSubscriber(
    influxdb_host='influxdb.example.com',
    influxdb_port=8086,
    influxdb_user='zmq',
    influxdb_password='zmq',
    influxdb_db='tick'
)

4.2 Creating Database
---------------------
# Using influx CLI
influx -host localhost -port 8086

> CREATE DATABASE tick
> CREATE USER zmq WITH PASSWORD 'zmq'
> GRANT ALL ON tick TO zmq

# Verify
> SHOW DATABASES
> SHOW USERS

4.3 Data Retention
------------------
# Set retention policy
> CREATE RETENTION POLICY "daily" ON "tick" 
  DURATION 1d 
  REPLICATION 1 
  DEFAULT

# Delete old data automatically
> ALTER RETENTION POLICY "daily" ON "tick" 
  DURATION 30d

5. NETWORK CONFIGURATION
========================

5.1 Local Network
-----------------
Services run on localhost:PORT by default

Publisher binds to: tcp://*:PORT (all interfaces)
Subscriber connects to: tcp://localhost:PORT

5.2 Remote Host
---------------
Subscriber on different host:

subscriber = KrakenTickToInfluxDBSubscriber(
    zmq_host='zmq.example.com'  # Publisher host
)

5.3 Docker/Container Setup
---------------------------
Services in containers can communicate via:

# Docker compose example
services:
  publisher:
    image: nbpy:latest
    command: nbpy-pub-kraken-tick
    ports:
      - "5558:5558"
    environment:
      - PYTHONUNBUFFERED=1
  
  subscriber:
    image: nbpy:latest
    command: nbpy-sub-kraken-influxdb-tick publisher influxdb
    depends_on:
      - publisher
    environment:
      - PYTHONUNBUFFERED=1
  
  influxdb:
    image: influxdb:1.8
    ports:
      - "8086:8086"
    environment:
      - INFLUXDB_DB=tick

6. SYSTEMD SERVICE SETUP
========================

6.1 Create Service File
-----------------------
# /etc/systemd/system/nbpy-kraken-tick.service

[Unit]
Description=NBPY Kraken Tick Publisher
After=network.target

[Service]
Type=simple
User=zmq
Group=zmq
WorkingDirectory=/opt/nbpy
ExecStart=/opt/nbpy/venv/bin/nbpy-pub-kraken-tick
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

6.2 Enable Service
------------------
$ sudo systemctl daemon-reload
$ sudo systemctl enable nbpy-kraken-tick
$ sudo systemctl start nbpy-kraken-tick
$ sudo systemctl status nbpy-kraken-tick

# View logs
$ sudo journalctl -u nbpy-kraken-tick -f

7. PERFORMANCE TUNING
====================

7.1 Socket Buffer Sizes
-----------------------
from nbpy.zmq import BasePublisher
import zmq

publisher = BasePublisher(port_config)

# Increase send high water mark (default ~1000)
publisher.socket.setsockopt(zmq.SNDHWM, 10000)

# Decrease linger to avoid hang on close
publisher.socket.setsockopt(zmq.LINGER, 0)

7.2 Message Batching
--------------------
Instead of:
  for data in data_list:
      pub.publish_json(topic, data)  # Slow!

Do:
  batch = []
  for data in data_list:
      batch.append(data)
      if len(batch) >= 100:
          pub.publish_json(topic, batch)
          batch = []

7.3 Publisher Slow Subscriber Pattern
-------------------------------------
If subscribers are slow, use PUSH/PULL instead of PUB/SUB:

# Publisher
socket = context.socket(zmq.PUSH)
socket.bind("tcp://*:5558")

# Subscriber
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5558")

This ensures no message loss when subscriber is slow.

7.4 Connection Optimization
----------------------------
# Reuse context across services
import zmq
context = zmq.Context()

pub1 = BasePublisher(config1, context=context)
pub2 = BasePublisher(config2, context=context)

# Close context at end
context.term()

8. MONITORING AND HEALTH
=========================

8.1 Service Health Check
------------------------
# Check if port is listening
$ lsof -i :5558

# Check ZMQ socket stats
$ netstat -an | grep 5558

# Monitor with top
$ top -p $(pgrep -f nbpy)

8.2 Message Throughput
----------------------
Add message counter:

class MonitoredPublisher(BasePublisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_count = 0
    
    def publish_json(self, *args, **kwargs):
        super().publish_json(*args, **kwargs)
        self.message_count += 1
        if self.message_count % 1000 == 0:
            logger.info(f"Published {self.message_count} messages")

8.3 InfluxDB Query Monitoring
-----------------------------
# Connect to influx CLI
$ influx -host localhost

# Query recent data
> SELECT * FROM tick WHERE time > now() - 1h LIMIT 100

# Check measurements
> SHOW MEASUREMENTS

# Database stats
> SHOW STATS

9. SECURITY CONSIDERATIONS
==========================

9.1 Authentication
------------------
# ZMQ doesn't provide built-in auth, use network isolation

# InfluxDB authentication
# Always use credentials (zmq/zmq is example)

9.2 Network Isolation
---------------------
# Restrict ZMQ ports to trusted hosts
$ sudo ufw allow from 192.168.1.0/24 to any port 5558

# Use VPN for remote access
# Or SSH tunneling:
$ ssh -L 5558:zmq.local:5558 bastion.host.com

9.3 Data Validation
-------------------
# Always validate received data
try:
    topic, data = sub.recv_msgpack()
    if 'required_field' not in data:
        logger.warning(f"Invalid message: {data}")
        continue
except Exception as e:
    logger.error(f"Deserialization error: {e}")

10. TROUBLESHOOTING
==================

10.1 Port Already in Use
------------------------
# Find process using port
$ lsof -i :5558
$ netstat -tlnp | grep 5558

# Kill if needed
$ kill -9 <PID>

10.2 Connection Issues
----------------------
# Test connectivity
$ nc -zv localhost 5558
$ telnet localhost 5558

# Check firewall
$ sudo ufw status
$ sudo iptables -L -n

10.3 InfluxDB Connection Error
------------------------------
# Test InfluxDB connectivity
$ curl http://localhost:8086/ping

# Check InfluxDB logs
$ journalctl -u influxdb -f

# Verify credentials
$ influx -host localhost -username zmq -password zmq

10.4 MessagePack Errors
-----------------------
# Ensure both sides use msgpack
# Check message format in logs

# Test msgpack
>>> import msgpack
>>> msgpack.packb({'test': 'data'})
b'\\x81\\xa4test\\xa4data'

11. DEPLOYMENT CHECKLIST
======================

□ Install dependencies (msgpack, influxdb, pyzmq)
□ Run validation tests (python3 -m nbpy.zmq.validate)
□ Configure InfluxDB database and user
□ Test network connectivity between services
□ Set up logging (file/syslog/ELK)
□ Configure systemd service files
□ Set resource limits (ulimit, cgroups)
□ Enable monitoring/alerting
□ Document port assignments
□ Set up backup for InfluxDB
□ Create runbook for operations
□ Plan for scaling (sharding, load balancing)

12. ADDITIONAL RESOURCES
=======================

Documentation:
  - nbpy/zmq/README.md - Module documentation
  - nbpy/zmq/MIGRATION_GUIDE.md - Migration guide
  - nbpy/zmq/validate.py - Validation code

External:
  - ZMQ Guide: https://zguide.zeromq.org/
  - MessagePack: https://msgpack.org/
  - InfluxDB: https://docs.influxdata.com/
  - Python Logging: https://docs.python.org/3/library/logging.html

================================================================================
"""


if __name__ == '__main__':
    print(get_configuration_guide())
