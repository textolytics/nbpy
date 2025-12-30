#!/usr/bin/env python3
"""Verification script for nbpy_zmq installation and setup."""

import sys
from pathlib import Path


def check_imports():
    """Check that all core imports work."""
    print("\n" + "="*60)
    print("Checking Core Imports")
    print("="*60)
    
    try:
        from nbpy_zmq.utils import ZMQConfig, MessageBus
        print("✓ nbpy_zmq.utils.ZMQConfig")
        print("✓ nbpy_zmq.utils.MessageBus")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    try:
        import zmq
        print("✓ zmq (pyzmq)")
    except ImportError:
        print("✗ zmq (pyzmq) not found")
        return False
    
    try:
        from influxdb import InfluxDBClient
        print("✓ influxdb.InfluxDBClient")
    except ImportError:
        print("✗ influxdb not found")
        return False
    
    try:
        import ccs
        print("✓ ccs (Kraken wrapper)")
    except ImportError:
        print("✗ ccs not found")
        return False
    
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        print("✓ vaderSentiment.SentimentIntensityAnalyzer")
    except ImportError:
        print("✗ vaderSentiment not found")
        return False
    
    return True


def check_configuration():
    """Check ZMQConfig defaults."""
    print("\n" + "="*60)
    print("Checking Configuration")
    print("="*60)
    
    from nbpy_zmq.utils import ZMQConfig
    
    config = ZMQConfig()
    
    checks = [
        ("ZMQ Host", config.host, "localhost"),
        ("ZMQ Pub Port", config.pub_port, 5559),
        ("ZMQ Sub Port", config.sub_port, 5560),
        ("InfluxDB Host", config.influxdb_host, "192.168.0.33"),
        ("InfluxDB Port", config.influxdb_port, 8086),
        ("InfluxDB DB", config.influxdb_db, "tick"),
        ("Default Kraken Topic", config.default_kraken_tick_topic, "kr_eurusd_tick"),
    ]
    
    all_ok = True
    for name, actual, expected in checks:
        if actual == expected:
            print(f"✓ {name}: {actual}")
        else:
            print(f"✗ {name}: {actual} (expected {expected})")
            all_ok = False
    
    return all_ok


def check_message_bus():
    """Check MessageBus initialization."""
    print("\n" + "="*60)
    print("Checking MessageBus")
    print("="*60)
    
    try:
        from nbpy_zmq.utils import ZMQConfig, MessageBus
        
        config = ZMQConfig()
        bus = MessageBus(config)
        
        print("✓ MessageBus initialization")
        print(f"✓ Config attached: {bus.config is not None}")
        print(f"✓ ZMQ context created: {bus.context is not None}")
        
        bus.close()
        print("✓ MessageBus cleanup")
        
        return True
    except Exception as e:
        print(f"✗ MessageBus check failed: {e}")
        return False


def check_project_structure():
    """Check that project files exist."""
    print("\n" + "="*60)
    print("Checking Project Structure")
    print("="*60)
    
    project_root = Path(__file__).parent
    
    required_files = [
        "nbpy_zmq/__init__.py",
        "nbpy_zmq/utils/__init__.py",
        "nbpy_zmq/utils/config.py",
        "nbpy_zmq/utils/message_bus.py",
        "nbpy_zmq/publishers/__init__.py",
        "nbpy_zmq/subscribers/__init__.py",
        "nbpy_zmq/forwarders/__init__.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        "INDEX.md",
        "tests/test_core.py",
    ]
    
    all_ok = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            all_ok = False
    
    return all_ok


def main():
    """Run all verification checks."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "nbpy_zmq Installation Verification" + " "*9 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run checks
    results.append(("Project Structure", check_project_structure()))
    results.append(("Core Imports", check_imports()))
    results.append(("Configuration", check_configuration()))
    results.append(("MessageBus", check_message_bus()))
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    for check_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} — {check_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("✓ Project is ready for development")
        print("="*60 + "\n")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("✗ Please review the errors above")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
