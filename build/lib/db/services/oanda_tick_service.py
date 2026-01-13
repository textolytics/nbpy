#!/usr/bin/env python3
"""
OANDA Tick Data to InfluxDB Service

Subscribes to OANDA tick data from ZMQ publisher and stores to InfluxDB.
"""

import sys
import signal
import logging
from pathlib import Path

# Add nbpy to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db import create_oanda_bridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run OANDA tick to InfluxDB service"""
    logger.info("Starting OANDA Tick to InfluxDB Service")
    logger.info("Subscribing to ZMQ port 5556 (oanda_tick)")
    
    # Create bridge
    bridge = create_oanda_bridge(zmq_port=5556)
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        bridge.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run bridge (blocking)
        bridge.run(blocking=True)
    except Exception as e:
        logger.error(f"Error running bridge: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
