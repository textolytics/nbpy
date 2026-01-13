#!/usr/bin/env python3
"""
Health Check and Status Monitoring Service

Monitors the InfluxDB service and reports statistics.
"""

import sys
import logging
from pathlib import Path
import time

# Add nbpy to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db import InfluxDBService, get_config_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_connection():
    """Check InfluxDB connection"""
    service = InfluxDBService()
    
    if not service.client:
        logger.error("✗ Cannot connect to InfluxDB")
        return False
    
    logger.info("✓ Connected to InfluxDB")
    
    # Get databases
    try:
        databases = service.client.get_list_database()
        db_names = [db['name'] for db in databases]
        logger.info(f"  Available databases: {', '.join(db_names)}")
    except Exception as e:
        logger.error(f"  Error listing databases: {e}")
    
    service.close()
    return True


def check_configuration():
    """Check configuration"""
    logger.info("\nConfiguration Check:")
    
    config_mgr = get_config_manager()
    base_config = config_mgr.get_base_config()
    
    logger.info(f"  Host: {base_config.get('host', 'N/A')}")
    logger.info(f"  Port: {base_config.get('port', 'N/A')}")
    logger.info(f"  Database: {base_config.get('database', 'N/A')}")
    logger.info(f"  Batch size: {base_config.get('batch_size', 'N/A')}")
    logger.info(f"  Timeout: {base_config.get('timeout', 'N/A')}")


def check_write_capability():
    """Test write capability"""
    logger.info("\nWrite Capability Check:")
    
    from db import TickData
    
    service = InfluxDBService()
    
    try:
        tick = TickData(
            instrument="TEST_HEALTH_CHECK",
            bid=1.0000,
            ask=1.0001
        )
        
        service.write_point(tick)
        service.flush(force=True)
        
        logger.info("  ✓ Successfully wrote test data")
        
    except Exception as e:
        logger.error(f"  ✗ Write failed: {e}")
    finally:
        service.close()


def main():
    """Run health checks"""
    logger.info("=" * 60)
    logger.info("InfluxDB Service Health Check")
    logger.info("=" * 60)
    
    # Run checks
    connection_ok = check_connection()
    check_configuration()
    
    if connection_ok:
        check_write_capability()
    
    logger.info("\n" + "=" * 60)
    logger.info("Health check completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
