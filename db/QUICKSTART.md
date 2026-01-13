#!/usr/bin/env python3
"""
Quick Start Guide for nbpy Database Module

This script provides quick-start examples and setup instructions.
"""

import sys
from pathlib import Path

# Add nbpy to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def show_installation():
    """Show installation instructions"""
    print_section("Installation")
    print("""
1. Install required packages:
   pip install influxdb zmq

2. Configure environment:
   Create .env file in /home/textolytics/nbpy/:
   
   INFLUXDB_HOST=localhost
   INFLUXDB_PORT=8086
   INFLUXDB_USER=zmq
   INFLUXDB_PASSWORD=zmq
   INFLUXDB_DB=tick

3. Verify installation:
   python3 -c "from nbpy.db import InfluxDBService; print('OK' if InfluxDBService().client else 'FAILED')"
    """)


def show_basic_usage():
    """Show basic usage example"""
    print_section("Basic Usage")
    print("""
from nbpy.db import InfluxDBService, TickData

# Create service
service = InfluxDBService()

# Create data
tick = TickData(
    instrument="EURUSD",
    bid=1.0856,
    ask=1.0858,
    base_ccy="EUR",
    term_ccy="USD"
)

# Write to InfluxDB
service.write_point(tick)
service.flush(force=True)

# Close
service.close()
    """)


def show_zmq_bridge():
    """Show ZMQ bridge usage"""
    print_section("ZMQ Bridge Usage")
    print("""
from nbpy.db import create_kraken_bridge

# Create and run Kraken bridge
bridge = create_kraken_bridge(zmq_port=5558)

# Run in current thread (blocking)
bridge.run(blocking=True)

# Or run in background
bridge.run(blocking=False)

# When done
bridge.stop()
    """)


def show_file_structure():
    """Show file structure"""
    print_section("File Structure")
    print("""
/home/textolytics/nbpy/db/
├── __init__.py                    # Package initialization
├── influxdb_service.py            # Core InfluxDB service
├── config.py                      # Configuration management
├── zmq_influxdb_bridge.py         # ZMQ integration
├── examples.py                    # Usage examples
├── README.md                      # Documentation
├── INTEGRATION_GUIDE.md           # Integration instructions
├── QUICKSTART.md                  # This file
└── services/                      # Ready-to-use services
    ├── kraken_tick_service.py     # Kraken → InfluxDB
    ├── oanda_tick_service.py      # OANDA → InfluxDB
    └── health_check.py            # System health check
    """)


def show_services():
    """Show available services"""
    print_section("Available Services")
    print("""
1. Kraken Tick Service
   python3 /home/textolytics/nbpy/db/services/kraken_tick_service.py

2. OANDA Tick Service
   python3 /home/textolytics/nbpy/db/services/oanda_tick_service.py

3. Health Check
   python3 /home/textolytics/nbpy/db/services/health_check.py

4. Examples
   python3 /home/textolytics/nbpy/db/examples.py
    """)


def show_commands():
    """Show common commands"""
    print_section("Common Commands")
    print("""
# Check connection
python3 -c "from nbpy.db import InfluxDBService; s = InfluxDBService(); print('OK' if s.client else 'FAIL')"

# Run health check
python3 /home/textolytics/nbpy/db/services/health_check.py

# Start Kraken bridge
python3 /home/textolytics/nbpy/db/services/kraken_tick_service.py

# Start OANDA bridge
python3 /home/textolytics/nbpy/db/services/oanda_tick_service.py

# Run all examples
python3 /home/textolytics/nbpy/db/examples.py

# Query data
python3 << 'EOF'
from nbpy.db import InfluxDBService
s = InfluxDBService()
tick = s.get_latest_tick("EURUSD")
print(tick)
s.close()
EOF
    """)


def show_configuration():
    """Show configuration options"""
    print_section("Configuration Options")
    print("""
Environment Variables:
  INFLUXDB_HOST          InfluxDB server hostname
  INFLUXDB_PORT          InfluxDB server port
  INFLUXDB_USER          InfluxDB username
  INFLUXDB_PASSWORD      InfluxDB password
  INFLUXDB_DB            Database name
  INFLUXDB_SSL           Use SSL (true/false)
  INFLUXDB_VERIFY_SSL    Verify SSL certificate (true/false)
  INFLUXDB_TIMEOUT       Connection timeout in seconds
  INFLUXDB_BATCH_SIZE    Number of points per batch write
  INFLUXDB_CONSISTENCY   Write consistency level
  INFLUXDB_RETENTION     Retention policy name

Configuration Precedence:
  1. Environment variables (highest priority)
  2. .env file in current directory
  3. .env file in /home/textolytics/nbpy/
  4. Built-in defaults (lowest priority)
    """)


def show_troubleshooting():
    """Show troubleshooting tips"""
    print_section("Troubleshooting")
    print("""
Problem: "Cannot connect to InfluxDB"
Solution:
  1. Check InfluxDB is running: systemctl status influxdb
  2. Verify host and port: telnet localhost 8086
  3. Check credentials: curl -u zmq:zmq http://localhost:8086/ping

Problem: "Data not appearing in InfluxDB"
Solution:
  1. Check database exists: python3 -c "from nbpy.db import InfluxDBService; s = InfluxDBService(); print(s.client.get_list_database())"
  2. Check write_points is returning True
  3. Check service.flush() is called

Problem: "Permission denied"
Solution:
  1. Ensure correct file permissions
  2. Run as correct user: sudo -u textolytics python3 script.py
  3. Check InfluxDB user permissions

Problem: "ModuleNotFoundError: No module named 'influxdb'"
Solution:
  pip install influxdb zmq
    """)


def main():
    """Show quick start guide"""
    print("\n" + "=" * 70)
    print("  nbpy Database Module - Quick Start Guide")
    print("=" * 70)
    
    show_installation()
    show_basic_usage()
    show_zmq_bridge()
    show_file_structure()
    show_services()
    show_commands()
    show_configuration()
    show_troubleshooting()
    
    print_section("Next Steps")
    print("""
1. Install dependencies: pip install influxdb zmq
2. Configure InfluxDB connection: .env file
3. Run health check: python3 services/health_check.py
4. Start services: python3 services/kraken_tick_service.py
5. View data: python3 -c "from nbpy.db import InfluxDBService; ..."

For more information:
  - README.md: Comprehensive documentation
  - INTEGRATION_GUIDE.md: Integration with ZMQ services
  - examples.py: Working code examples
    """)
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
