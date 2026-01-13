#!/usr/bin/env python3
"""
InfluxDB Service Verification Script

Tests:
1. InfluxDB connectivity
2. Python module imports
3. Database creation and data writing
4. Configuration management
5. ZMQ bridge setup
"""

import sys
import logging
import socket
from pathlib import Path
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def test_influxdb_connectivity():
    """Test connection to InfluxDB"""
    print_header("Test 1: InfluxDB Connectivity")
    
    host = "localhost"
    port = 8086
    
    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        print_success(f"InfluxDB server is accessible at {host}:{port}")
        return True
    except (socket.timeout, socket.error) as e:
        print_error(f"Cannot connect to InfluxDB at {host}:{port}")
        print_info(f"Error: {e}")
        print_info("Make sure InfluxDB is running:")
        print_info("  ./influxdb_service.sh start")
        return False


def test_python_imports():
    """Test Python module imports"""
    print_header("Test 2: Python Module Imports")
    
    all_ok = True
    
    modules = [
        ('influxdb', 'InfluxDB client library'),
        ('zmq', 'ZMQ library'),
    ]
    
    for module, description in modules:
        try:
            __import__(module)
            print_success(f"{module:20} - {description}")
        except ImportError as e:
            print_error(f"{module:20} - {description}")
            print_info(f"Install with: pip install {module}")
            all_ok = False
    
    # Test nbpy.db imports
    try:
        from nbpy.db import (
            InfluxDBService,
            InfluxDBConfig,
            TickData,
            DepthData,
            OHLCData,
            SentimentData,
        )
        print_success("nbpy.db                - All classes imported")
    except ImportError as e:
        print_error("nbpy.db                - Import failed")
        print_info(f"Error: {e}")
        all_ok = False
    
    return all_ok


def test_influxdb_service():
    """Test InfluxDB service"""
    print_header("Test 3: InfluxDB Service")
    
    try:
        from nbpy.db import InfluxDBService, TickData
        
        logger.info("Creating InfluxDB service...")
        service = InfluxDBService()
        
        if not service.client:
            print_error("Failed to connect to InfluxDB")
            return False
        
        print_success("InfluxDB service created and connected")
        
        # Get statistics
        stats = service.get_stats()
        print_info(f"Connected database: {stats['database']}")
        print_info(f"Connection status: {'Active' if stats['connected'] else 'Inactive'}")
        
        # Test write
        logger.info("Writing test data...")
        tick = TickData(
            instrument="TEST_EURUSD",
            bid=1.0856,
            ask=1.0858,
            base_ccy="EUR",
            term_ccy="USD"
        )
        
        if service.write_point(tick):
            print_success("Test data point written to buffer")
            
            if service.flush(force=True):
                print_success("Test data flushed to InfluxDB")
            else:
                print_error("Failed to flush data to InfluxDB")
                return False
        else:
            print_error("Failed to write test data")
            return False
        
        service.close()
        return True
        
    except Exception as e:
        print_error(f"InfluxDB service test failed: {e}")
        logger.exception(e)
        return False


def test_configuration_management():
    """Test configuration management"""
    print_header("Test 4: Configuration Management")
    
    try:
        from nbpy.db.config import get_config_manager, InfluxDBConfig
        
        # Test config manager
        logger.info("Loading configuration manager...")
        config_mgr = get_config_manager()
        
        base_config = config_mgr.get_base_config()
        print_success("Base configuration loaded")
        print_info(f"Configuration keys: {list(base_config.keys())}")
        
        # Test service-specific config
        tick_config = config_mgr.get_service_config('tick')
        print_success("Service-specific config loaded (tick)")
        print_info(f"Tick database: {tick_config.get('database', 'N/A')}")
        
        # Test custom config
        logger.info("Creating custom configuration...")
        custom_config = InfluxDBConfig(
            host="localhost",
            port=8086,
            database="test_db",
            batch_size=100
        )
        print_success("Custom configuration created")
        print_info(f"Custom host: {custom_config.host}:{custom_config.port}")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration management test failed: {e}")
        logger.exception(e)
        return False


def test_zmq_bridge_setup():
    """Test ZMQ bridge setup"""
    print_header("Test 5: ZMQ Bridge Setup")
    
    try:
        from nbpy.db.zmq_influxdb_bridge import (
            ZMQInfluxDBBridge,
            KrakenTickBridge,
            OandaTickBridge,
        )
        
        # Test bridge creation
        logger.info("Creating Kraken tick bridge...")
        kraken_bridge = KrakenTickBridge(zmq_port=5558)
        print_success("Kraken tick bridge created")
        print_info(f"Bridge topic filter: {kraken_bridge.topic_filter}")
        print_info(f"Bridge service name: {kraken_bridge.service_name}")
        
        # Test OANDA bridge
        logger.info("Creating OANDA tick bridge...")
        oanda_bridge = OandaTickBridge(zmq_port=5556)
        print_success("OANDA tick bridge created")
        print_info(f"Bridge topic filter: {oanda_bridge.topic_filter}")
        
        # Check if bridges are ready
        if kraken_bridge.influxdb_service.client:
            print_success("Bridges have active InfluxDB connections")
        else:
            print_warning("Bridges created but InfluxDB not fully connected")
        
        return True
        
    except Exception as e:
        print_error(f"ZMQ bridge setup test failed: {e}")
        logger.exception(e)
        return False


def test_data_models():
    """Test data models"""
    print_header("Test 6: Data Models")
    
    try:
        from nbpy.db import (
            TickData,
            DepthData,
            OHLCData,
            SentimentData,
            DataType,
        )
        
        # Test TickData
        logger.info("Creating TickData...")
        tick = TickData(
            instrument="EURUSD",
            bid=1.0856,
            ask=1.0858,
            base_ccy="EUR",
            term_ccy="USD",
            volume=1000000
        )
        tick_json = tick.to_influx_json()
        print_success("TickData created and converted to JSON")
        print_info(f"Measurement: {tick_json['measurement']}")
        
        # Test DepthData
        logger.info("Creating DepthData...")
        depth = DepthData(
            instrument="EURUSD",
            bid_prices=[1.0856, 1.0855],
            bid_volumes=[1000000, 500000],
            ask_prices=[1.0858, 1.0859],
            ask_volumes=[1000000, 500000]
        )
        depth_json = depth.to_influx_json()
        print_success("DepthData created and converted to JSON")
        
        # Test OHLCData
        logger.info("Creating OHLCData...")
        ohlc = OHLCData(
            instrument="EURUSD",
            open=1.0850,
            high=1.0860,
            low=1.0845,
            close=1.0858,
            volume=1000000,
            trades=5000
        )
        ohlc_json = ohlc.to_influx_json()
        print_success("OHLCData created and converted to JSON")
        
        # Test SentimentData
        logger.info("Creating SentimentData...")
        sentiment = SentimentData(
            source="twitter",
            instrument="EURUSD",
            sentiment_score=0.75,
            text="EUR is strengthening"
        )
        sentiment_json = sentiment.to_influx_json()
        print_success("SentimentData created and converted to JSON")
        
        # Test DataType enum
        print_success(f"Available DataTypes: {[dt.value for dt in DataType]}")
        
        return True
        
    except Exception as e:
        print_error(f"Data models test failed: {e}")
        logger.exception(e)
        return False


def test_file_structure():
    """Test file structure"""
    print_header("Test 7: File Structure")
    
    db_dir = Path(__file__).parent
    required_files = [
        'influxdb_service.py',
        'config.py',
        'zmq_influxdb_bridge.py',
        '__init__.py',
        'influxdb_service.sh',
        'init-databases.sh',
        'docker-compose.yml',
        'Dockerfile',
        'influxdb.service',
        'README.md',
        'INFLUXDB_SETUP.md',
    ]
    
    all_ok = True
    for filename in required_files:
        filepath = db_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print_success(f"{filename:30} ({size:,} bytes)")
        else:
            print_error(f"{filename:30} - NOT FOUND")
            all_ok = False
    
    return all_ok


def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.RESET}")
    if failed_tests > 0:
        print(f"{Colors.RED}Failed: {failed_tests}{Colors.RESET}")
    
    print("\nResults:")
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {test_name:40} {status}")
    
    print("\n" + "="*70)
    
    if failed_tests == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.RESET}")
        print("\nInfluxDB service is ready to use:")
        print("  1. Start service: ./influxdb_service.sh start")
        print("  2. Initialize databases: ./influxdb_service.sh init-db")
        print("  3. Use Python API: from nbpy.db import InfluxDBService")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some tests failed{Colors.RESET}")
        print("\nFix issues and run tests again:")
        print("  python3 verify_setup.py")
    
    print("="*70 + "\n")
    
    return failed_tests == 0


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}InfluxDB Service Verification{Colors.RESET}")
    print(f"Version 1.0.0 - {Path(__file__).parent.name}\n")
    
    results = {}
    
    # Run tests
    tests = [
        ("InfluxDB Connectivity", test_influxdb_connectivity),
        ("Python Imports", test_python_imports),
        ("InfluxDB Service", test_influxdb_service),
        ("Configuration Management", test_configuration_management),
        ("ZMQ Bridge Setup", test_zmq_bridge_setup),
        ("Data Models", test_data_models),
        ("File Structure", test_file_structure),
    ]
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Print summary
    all_passed = print_summary(results)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
