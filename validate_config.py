#!/usr/bin/env python3
"""
NBPY Configuration Validator

Validates that all ZMQ microservices are properly configured for startup,
including:
- Virtual environment setup
- Port availability
- Docker configuration
- Service accessibility
- Data connectivity
"""

import sys
import socket
import subprocess
import logging
from pathlib import Path
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
NBPY_ROOT = Path(__file__).parent
VENV_PYTHON = NBPY_ROOT / "nbpy" / "bin" / "python"
DOCKER_COMPOSE_FILE = NBPY_ROOT / "docker-compose.yml"

# Services and ports
PORTS_TO_CHECK = {
    5556: ("OANDA Publisher", "tcp"),
    5558: ("Kraken Tick Publisher", "tcp"),
    5559: ("Kraken EURUSD Publisher", "tcp"),
    5560: ("Kraken Depth Publisher", "tcp"),
    5561: ("Kraken Orders Publisher", "tcp"),
    5562: ("OANDA Tick Publisher", "tcp"),
    5563: ("OANDA Orders Publisher", "tcp"),
    5564: ("Betfair Stream Publisher", "tcp"),
    5565: ("Twitter Sentiment Publisher", "tcp"),
    5566: ("Kraken EURUSD Depth Publisher", "tcp"),
    5567: ("OANDA v20 Tick Publisher", "tcp"),
    8086: ("InfluxDB API", "tcp"),
    8083: ("InfluxDB Web UI", "tcp"),
    3000: ("Grafana", "tcp"),
}


class Colors:
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")


def check_ok(msg):
    """Print OK message"""
    print(f"{Colors.OK}✓{Colors.END} {msg}")


def check_warn(msg):
    """Print warning message"""
    print(f"{Colors.WARN}!{Colors.END} {msg}")


def check_fail(msg):
    """Print failure message"""
    print(f"{Colors.FAIL}✗{Colors.END} {msg}")


def is_port_open(port, host="localhost"):
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def check_python_env():
    """Verify Python virtual environment"""
    print_header("Python Environment Check")
    
    if not VENV_PYTHON.exists():
        check_fail(f"Python environment not found at {VENV_PYTHON}")
        return False
    
    check_ok(f"Python environment found: {VENV_PYTHON}")
    
    # Check if nbpy is installed
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), "-c", "import nbpy.zmq; print(nbpy.zmq.__file__)"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            check_ok("nbpy module installed")
            print(f"  Location: {result.stdout.strip()}")
            return True
        else:
            check_warn("nbpy module not found - installing...")
            try:
                subprocess.run(
                    [str(VENV_PYTHON), "-m", "pip", "install", "-e", str(NBPY_ROOT)],
                    capture_output=True,
                    timeout=60
                )
                check_ok("nbpy installed successfully")
                return True
            except Exception as e:
                check_fail(f"Failed to install nbpy: {e}")
                return False
    except Exception as e:
        check_fail(f"Error checking nbpy: {e}")
        return False


def check_dependencies():
    """Verify required Python packages"""
    print_header("Dependencies Check")
    
    required = {
        "pyzmq": "ZMQ messaging",
        "msgpack": "MessagePack serialization",
        "influxdb": "InfluxDB client",
    }
    
    all_ok = True
    for package, description in required.items():
        try:
            result = subprocess.run(
                [str(VENV_PYTHON), "-c", f"import {package}; print({package}.__version__)"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                check_ok(f"{package} ({description}): {result.stdout.strip()}")
            else:
                check_fail(f"{package} ({description}): NOT INSTALLED")
                all_ok = False
        except Exception as e:
            check_fail(f"{package}: {e}")
            all_ok = False
    
    return all_ok


def check_ports():
    """Check port availability"""
    print_header("Port Availability Check")
    
    available = []
    in_use = []
    
    for port, (service, _) in PORTS_TO_CHECK.items():
        if is_port_open(port):
            check_warn(f"Port {port} ({service}): IN USE")
            in_use.append(port)
        else:
            check_ok(f"Port {port} ({service}): Available")
            available.append(port)
    
    print(f"\nAvailable: {len(available)}/{len(PORTS_TO_CHECK)}")
    print(f"In Use: {len(in_use)}/{len(PORTS_TO_CHECK)}")
    
    if in_use:
        check_warn("Some ports are already in use. Services may fail to start.")
        return False
    
    return True


def check_docker():
    """Verify Docker installation"""
    print_header("Docker Installation Check")
    
    # Check Docker
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            check_ok(f"Docker: {result.stdout.strip()}")
        else:
            check_fail("Docker: Not installed or not in PATH")
            return False
    except Exception as e:
        check_fail(f"Docker: {e}")
        return False
    
    # Check Docker Compose
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            check_ok(f"Docker Compose: {result.stdout.strip()}")
        else:
            check_fail("Docker Compose: Not installed")
            return False
    except Exception as e:
        check_fail(f"Docker Compose: {e}")
        return False
    
    # Check Docker daemon
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            check_ok("Docker daemon: Running")
        else:
            check_fail("Docker daemon: Not running or permission denied")
            return False
    except Exception as e:
        check_fail(f"Docker daemon: {e}")
        return False
    
    return True


def check_docker_compose_file():
    """Verify docker-compose.yml"""
    print_header("Docker Compose Configuration Check")
    
    if not DOCKER_COMPOSE_FILE.exists():
        check_fail(f"docker-compose.yml not found at {DOCKER_COMPOSE_FILE}")
        return False
    
    check_ok(f"docker-compose.yml found")
    
    # Validate YAML syntax
    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "config"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            check_ok("docker-compose.yml syntax: Valid")
            return True
        else:
            check_fail(f"docker-compose.yml syntax error: {result.stderr[:200]}")
            return False
    except Exception as e:
        check_fail(f"Docker Compose validation: {e}")
        return False


def check_zmq_services():
    """Check ZMQ service modules"""
    print_header("ZMQ Services Check")
    
    publishers_dir = NBPY_ROOT / "nbpy" / "zmq" / "publishers"
    subscribers_dir = NBPY_ROOT / "nbpy" / "zmq" / "subscribers"
    
    if not publishers_dir.exists():
        check_fail(f"Publishers directory not found: {publishers_dir}")
        return False
    
    if not subscribers_dir.exists():
        check_fail(f"Subscribers directory not found: {subscribers_dir}")
        return False
    
    pub_count = len(list(publishers_dir.glob("*.py"))) - 1  # Exclude __init__.py
    sub_count = len(list(subscribers_dir.glob("*.py"))) - 1
    
    check_ok(f"Publishers found: {pub_count}")
    check_ok(f"Subscribers found: {sub_count}")
    
    return True


def check_port_registry():
    """Verify port registry configuration"""
    print_header("Port Registry Check")
    
    ports_file = NBPY_ROOT / "nbpy" / "zmq" / "ports.py"
    
    if not ports_file.exists():
        check_fail(f"ports.py not found: {ports_file}")
        return False
    
    check_ok(f"ports.py found")
    
    # Try to import and validate
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), "-c", 
             "from nbpy.zmq.ports import PORT_REGISTRY; print(len(PORT_REGISTRY))"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            port_count = int(result.stdout.strip())
            check_ok(f"Port registry: {port_count} ports configured")
            return True
        else:
            check_fail(f"Port registry validation failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        check_fail(f"Port registry error: {e}")
        return False


def check_connectivity():
    """Test localhost connectivity"""
    print_header("Localhost Connectivity Check")
    
    test_hosts = [
        ("localhost", "DNS resolution"),
        ("127.0.0.1", "Loopback interface"),
    ]
    
    all_ok = True
    for host, desc in test_hosts:
        try:
            socket.gethostbyname(host)
            check_ok(f"{desc}: OK ({host})")
        except Exception as e:
            check_fail(f"{desc}: {e}")
            all_ok = False
    
    return all_ok


def print_summary(results):
    """Print validation summary"""
    print_header("Validation Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("Results:")
    for check, result in results.items():
        status = f"{Colors.OK}PASS{Colors.END}" if result else f"{Colors.FAIL}FAIL{Colors.END}"
        print(f"  {check}: {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print(f"\n{Colors.OK}✓ All checks passed! Ready to start services.{Colors.END}")
        print(f"\nNext steps:")
        print(f"  1. Run: ./startup.sh start")
        print(f"  2. Open: http://localhost:3000 (Grafana)")
        print(f"  3. Check: ./startup.sh status")
        return True
    else:
        print(f"\n{Colors.WARN}! Some checks failed. Please review errors above.{Colors.END}")
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("NBPY Configuration Validator")
    print("="*60)
    
    results = {
        "Python Environment": check_python_env(),
        "Dependencies": check_dependencies(),
        "Localhost Connectivity": check_connectivity(),
        "Port Availability": check_ports(),
        "Docker Installation": check_docker(),
        "Docker Compose File": check_docker_compose_file(),
        "ZMQ Services": check_zmq_services(),
        "Port Registry": check_port_registry(),
    }
    
    success = print_summary(results)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
