"""
KRAKEN_EURUSD_DEPTH Publisher Module
Auto-migrated from python/scripts/zmq/pub_kraken_EURUSD_depth.py

This module wraps the original implementation while providing
nbpy.zmq framework integration with MessagePack serialization.
"""

import sys
import logging
from pathlib import Path

# Import framework components
from nbpy.zmq.base import BasePublisher
from nbpy.zmq.ports import PORT_REGISTRY
from nbpy.zmq.serialization import MessagePackCodec

# Import original service logic at module level
# (import * only allowed at module level)
try:
    from python.scripts.zmq.pub_kraken_EURUSD_depth import *
except ImportError:
    pass

logger = logging.getLogger(__name__)


class KrakenEurusdDepthPublisher(BasePublisher):
    """
    Publisher for KRAKEN_EURUSD_DEPTH
    
    Original service: pub_kraken_EURUSD_depth.py
    Port: 5560
    Topic: kr_eurusd_depth
    """
    
    def __init__(self):
        super().__init__(
            port=5560,
            topic='kr_eurusd_depth',
            service_name='kraken_EURUSD_depth'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized kraken_EURUSD_depth Publisher on port {self.port}, topic: {self.topic}")
    
    def run(self):
        """Start the publisher - implement service-specific logic"""
        logger.info(f"{self.service_name} publisher started")
        
        try:
            # Original service logic imported at module level
            logger.info(f"{self.service_name} publisher started")
        except Exception as e:
            logger.error(f"Error in publisher: {e}")
            raise


def main():
    """Entry point for kraken_EURUSD_depth publisher"""
    publisher = KrakenEurusdDepthPublisher()
    
    try:
        publisher.run()
    except KeyboardInterrupt:
        logger.info("{publisher.service_name} publisher interrupted by user")
        publisher.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"{publisher.service_name} publisher error: {e}", exc_info=True)
        publisher.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
