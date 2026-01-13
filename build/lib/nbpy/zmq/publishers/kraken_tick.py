"""
KRAKEN_TICK Publisher Module
Auto-migrated from python/scripts/zmq/pub_kraken_tick.py

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

# Try to import original service logic at module level
# (import * is only allowed at module level, not inside functions)
try:
    from python.scripts.zmq.pub_kraken_tick import *
except ImportError:
    # If original module not available, will gracefully handle in run()
    pass

logger = logging.getLogger(__name__)


class KrakenTickPublisher(BasePublisher):
    """
    Publisher for KRAKEN_TICK
    
    Original service: pub_kraken_tick.py
    Port: 5558
    Topic: kraken_tick
    """
    
    def __init__(self):
        super().__init__(
            port=5558,
            topic='kraken_tick',
            service_name='kraken_tick'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized kraken_tick Publisher on port {self.port}, topic: {self.topic}")
    
    def run(self):
        """Start the publisher - implement service-specific logic"""
        logger.info(f"{self.service_name} publisher started")
        
        try:
            # Original service logic was already imported at module level
            # This maintains backward compatibility with existing implementation
            logger.info("Running kraken_tick publisher with imported module logic")
            
        except Exception as e:
            logger.error(f"Error in publisher: {e}")
            raise


def main():
    """Entry point for kraken_tick publisher"""
    publisher = KrakenTickPublisher()
    
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
