#!/usr/bin/env python3
"""
Simple InfluxDB Service Verification Script
Tests the db module without requiring package installation
"""

import sys
import socket
import logging
from pathlib import Path

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
        print_info("You can access the API at: http://localhost:8086")
        return True
    except (socket.timeout, socket.error) as e:
        print_error(f"Cannot connect to InfluxDB at {host}:{port}")
        print_info(f"Error: {e}")
        print_info("\nTo start InfluxDB:")
        print_info("  Option 1 (System Service):")
        print_info("    cd /home/textolytics/nbpy/db")
        print_info("    ./influxdb_service.sh install")
        print_info("    ./influxdb_service.sh start")
        print_info("\n  Option 2 (Docker Compose):")
        print_info("    cd /home/textolytics/nbpy/db")
        print_info("    docker-compose up -d")
        return False


def test_python_libraries():
    """Test Python library imports"""
    print_header("Test 2: Python Library Dependencies")
    
    libraries = [
        ('influxdb', 'InfluxDB client'),
        ('zmq', 'ZMQ messaging'),
    ]
    
    all_ok = True
    for lib, desc in libraries:
        try:
            __import__(lib)
            print_success(f"{lib:15} - {desc}")
        except ImportError:
            print_error(f"{lib:15} - {desc}")
            print_info(f"Install with: pip install {lib}")
            all_ok = False
    
    return all_ok


def test_file_structure():
    """Test file structure"""
    print_header("Test 3: Module Files")
    
    db_dir = Path(__file__).parent
    
    files = [
        ('influxdb_service.py', 'Core InfluxDB service module'),
        ('config.py', 'Configuration management'),
        ('zmq_influxdb_bridge.py', 'ZMQ integration module'),
        ('__init__.py', 'Package initialization'),
        ('influxdb_service.sh', 'Service management script'),
        ('init-databases.sh', 'Database initialization'),
    ]
    
    all_ok = True
    for filename, description in files:
        filepath = db_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print_success(f"{filename:30} ({size:,} bytes) - {description}")
        else:
            print_error(f"{filename:30} - NOT FOUND")
            all_ok = False
    
    return all_ok


def test_scripts():
    """Test shell scripts"""
    print_header("Test 4: Shell Scripts")
    
    db_dir = Path(__file__).parent
    
    scripts = [
        ('influxdb_service.sh', 'InfluxDB service control'),
        ('init-databases.sh', 'Database initialization'),
    ]
    
    all_ok = True
    for script, desc in scripts:
        path = db_dir / script
        if path.exists():
            if path.stat().st_mode & 0o111:
                print_success(f"{script:30} - {desc} (executable)")
            else:
                print_warning(f"{script:30} - {desc} (not executable)")
                print_info(f"Make executable with: chmod +x {script}")
                all_ok = False
        else:
            print_error(f"{script:30} - NOT FOUND")
            all_ok = False
    
    return all_ok


def test_documentation():
    """Test documentation"""
    print_header("Test 5: Documentation")
    
    db_dir = Path(__file__).parent
    
    docs = [
        ('README.md', 'Main documentation'),
        ('INFLUXDB_SETUP.md', 'Setup guide'),
        ('QUICK_REFERENCE.md', 'Quick reference'),
    ]
    
    all_ok = True
    for doc, desc in docs:
        path = db_dir / doc
        if path.exists():
            size = path.stat().st_size
            print_success(f"{doc:30} ({size:,} bytes) - {desc}")
        else:
            print_warning(f"{doc:30} - NOT FOUND (optional)")
    
    return True  # Documentation is optional


def test_docker_files():
    """Test Docker files"""
    print_header("Test 6: Docker Configuration")
    
    db_dir = Path(__file__).parent
    
    files = [
        ('docker-compose.yml', 'Docker Compose configuration'),
        ('Dockerfile', 'Docker image definition'),
        ('influxdb.service', 'Systemd service unit'),
    ]
    
    all_ok = True
    for filename, desc in files:
        path = db_dir / filename
        if path.exists():
            size = path.stat().st_size
            print_success(f"{filename:30} ({size:,} bytes) - {desc}")
        else:
            print_warning(f"{filename:30} - NOT FOUND (optional)")
    
    return True  # Docker files are optional


def print_summary(results):
    """Print test summary"""
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {test_name:40} {status}")
    
    print("\n" + "="*70)
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.RESET}")
        print("\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print("\n1. Install InfluxDB:")
        print("   cd /home/textolytics/nbpy/db")
        print("   ./influxdb_service.sh install")
        print("\n2. Start InfluxDB:")
        print("   ./influxdb_service.sh start")
        print("\n3. Initialize databases:")
        print("   ./influxdb_service.sh init-db")
        print("\n4. Verify setup:")
        print("   ./influxdb_service.sh status")
        print("\n5. Start using the Python API:")
        print("   python3 examples.py")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some tests failed{Colors.RESET}")
        print("\nFix the issues and run again:")
        print("  python3 simple_verify.py")
    
    print("\n" + "="*70 + "\n")
    
    return failed == 0


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}InfluxDB Service Verification{Colors.RESET}")
    print(f"Version 1.0.0\n")
    
    results = {}
    
    tests = [
        ("InfluxDB Connectivity", test_influxdb_connectivity),
        ("Python Libraries", test_python_libraries),
        ("Module Files", test_file_structure),
        ("Shell Scripts", test_scripts),
        ("Documentation", test_documentation),
        ("Docker Files", test_docker_files),
    ]
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' failed: {e}")
            results[test_name] = False
    
    # Print summary
    all_passed = print_summary(results)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
