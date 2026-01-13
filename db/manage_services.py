#!/usr/bin/env python
"""
Docker Service Management Script for nbpy

This script provides utilities to:
- Stop running docker services
- Remove containers and volumes
- Recreate services with default configuration
- Verify service health

Usage:
    python manage_services.py stop
    python manage_services.py remove
    python manage_services.py create
    python manage_services.py reset      # Stop, remove, and create
    python manage_services.py health
    python manage_services.py status
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default compose file location
COMPOSE_FILE = Path(__file__).parent / 'docker-compose.yml'
COMPOSE_DIR = COMPOSE_FILE.parent


def run_command(cmd: list, description: str = None) -> Tuple[int, str, str]:
    """
    Run a shell command and return exit code and output.
    
    Args:
        cmd: Command as list of strings
        description: Optional description of what command does
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    if description:
        logger.info(f"Executing: {description}")
    
    logger.debug(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(COMPOSE_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.debug(f"STDERR:\n{result.stderr}")
        
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after 60 seconds: {' '.join(cmd)}")
        return 1, "", "Command timeout"
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return 1, "", str(e)


def stop_services() -> bool:
    """
    Stop all running docker-compose services.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("STOPPING SERVICES")
    logger.info("=" * 60)
    
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "stop"],
        "Stopping docker-compose services"
    )
    
    if exit_code == 0:
        logger.info("✓ Services stopped successfully")
        return True
    else:
        logger.error(f"✗ Failed to stop services: {stderr}")
        return False


def remove_services() -> bool:
    """
    Remove stopped containers and volumes.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("REMOVING CONTAINERS AND VOLUMES")
    logger.info("=" * 60)
    
    # Remove containers
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "rm", "-f"],
        "Removing docker-compose containers"
    )
    
    if exit_code != 0:
        logger.error(f"✗ Failed to remove containers: {stderr}")
        return False
    
    logger.info("✓ Containers removed successfully")
    
    # Remove volumes
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "down", "-v"],
        "Removing docker volumes"
    )
    
    if exit_code == 0:
        logger.info("✓ Volumes removed successfully")
        return True
    else:
        logger.warning(f"Note: Volume removal had issues: {stderr}")
        # Don't fail here - might be permission or other non-critical issue
        return True


def create_services() -> bool:
    """
    Create and start new services with default configuration.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 60)
    logger.info("CREATING AND STARTING SERVICES")
    logger.info("=" * 60)
    
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "up", "-d"],
        "Creating and starting docker-compose services"
    )
    
    if exit_code == 0:
        logger.info("✓ Services created and started successfully")
        logger.info("\nServices starting up, waiting for health checks...")
        time.sleep(10)  # Give services time to start
        return True
    else:
        logger.error(f"✗ Failed to create services: {stderr}")
        return False


def check_health() -> bool:
    """
    Check health of running services.
    
    Returns:
        True if all services are healthy, False otherwise
    """
    logger.info("=" * 60)
    logger.info("CHECKING SERVICE HEALTH")
    logger.info("=" * 60)
    
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "ps"],
        "Checking service status"
    )
    
    logger.info(stdout)
    
    # Check influxdb health
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "exec", "-T", "influxdb", "curl", "-f", "-u", "zmq:zmq", "http://localhost:8086/ping"],
        "Checking InfluxDB health"
    )
    
    if exit_code == 0:
        logger.info("✓ InfluxDB is healthy")
    else:
        logger.warning(f"⚠ InfluxDB health check failed: {stderr}")
    
    return exit_code == 0


def get_status() -> bool:
    """
    Get status of all services.
    
    Returns:
        True if output was successful
    """
    logger.info("=" * 60)
    logger.info("SERVICE STATUS")
    logger.info("=" * 60)
    
    exit_code, stdout, stderr = run_command(
        ["docker-compose", "ps"],
        "Getting service status"
    )
    
    logger.info(stdout)
    
    # Also show container logs summary
    logger.info("\nRecent container logs:")
    
    containers = ["influxdb", "grafana"]
    for container in containers:
        exit_code, stdout, stderr = run_command(
            ["docker-compose", "logs", "--tail=5", container],
            f"Getting {container} logs"
        )
        
        if exit_code == 0:
            logger.info(f"\n{container.upper()} logs (last 5 lines):")
            logger.info(stdout)
    
    return True


def reset_services() -> bool:
    """
    Full reset: stop, remove, and recreate services.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("\n" + "=" * 60)
    logger.info("FULL SERVICE RESET")
    logger.info("=" * 60 + "\n")
    
    logger.info("Default credentials being applied: zmq:zmq")
    logger.info("Default database: tick")
    logger.info("Services: influxdb (port 8086), grafana (port 3000)\n")
    
    # Step 1: Stop
    if not stop_services():
        logger.error("Failed to stop services")
        return False
    
    time.sleep(2)
    
    # Step 2: Remove
    if not remove_services():
        logger.error("Failed to remove services")
        return False
    
    time.sleep(2)
    
    # Step 3: Create
    if not create_services():
        logger.error("Failed to create services")
        return False
    
    # Step 4: Wait and check health
    logger.info("\nWaiting for services to be ready...")
    time.sleep(10)
    
    if check_health():
        logger.info("\n" + "=" * 60)
        logger.info("✓ RESET COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("\nServices are ready:")
        logger.info("  InfluxDB: http://localhost:8086")
        logger.info("  Grafana:  http://localhost:3000")
        logger.info("\nCredentials: zmq / zmq")
        return True
    else:
        logger.warning("\n" + "=" * 60)
        logger.warning("⚠ Reset completed but health check failed")
        logger.warning("=" * 60)
        logger.warning("\nServices may still be starting up. Try again in a moment.")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    # Check if docker-compose file exists
    if not COMPOSE_FILE.exists():
        logger.error(f"docker-compose.yml not found at {COMPOSE_FILE}")
        sys.exit(1)
    
    logger.info(f"Using docker-compose file: {COMPOSE_FILE}")
    
    # Execute command
    success = False
    
    if command == "stop":
        success = stop_services()
    elif command == "remove":
        success = remove_services()
    elif command == "create":
        success = create_services()
    elif command == "reset":
        success = reset_services()
    elif command == "health":
        success = check_health()
    elif command == "status":
        success = get_status()
    else:
        logger.error(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
