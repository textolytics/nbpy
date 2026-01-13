"""
KRAKEN_EURUSD_DEPTH Subscriber Module
Auto-migrated from python/scripts/zmq/sub_kraken_EURUSD_depth.py

This module wraps the original implementation while providing
nbpy.zmq framework integration with MessagePack deserialization.
"""

import sys
import logging
from pathlib import Path

# Import framework components
from nbpy.zmq.base import BaseSubscriber, BaseSubscriber
from nbpy.zmq.ports import PORT_REGISTRY
from nbpy.zmq.serialization import MessagePackCodec

logger = logging.getLogger(__name__)


class KrakenEurusdDepthSubscriber(BaseSubscriber):
    """
    Subscriber for KRAKEN_EURUSD_DEPTH
    
    Original service: sub_kraken_EURUSD_depth.py
    Connection port: 5558
    Topic filter: 1
    Backend type: generic
    """
    
    def __init__(self, connection_port=5558, topic_filter='1'):
        super().__init__(
            connection_port=connection_port,
            topic_filter=topic_filter,
            service_name='kraken_EURUSD_depth'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized kraken_EURUSD_depth Subscriber on port {self.connection_port}, topic: {self.topic_filter}")
    
    def process_message(self, topic, data):
        """Process incoming message - implement service-specific logic"""
        try:
            # Deserialize MessagePack data
            message = self.codec.unpack(data)
            
            # Import and run original service logic
            from python.scripts.zmq.sub_kraken_EURUSD_depth import process_message
            
            # Call original processor
            process_message(topic, message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise
    
    def run(self):
        """Start the subscriber - implement service-specific logic"""
        logger.info(f"{self.service_name} subscriber started")
        
        try:
            # Import and run original service logic
            from python.scripts.zmq.sub_kraken_EURUSD_depth import run
            
            run()
            
        except ImportError:
            logger.error(f"Could not import original module: sub_kraken_EURUSD_depth")
            logger.info("Please ensure python/scripts/zmq/ is in your PYTHONPATH")
            # Fall back to base implementation
            super().run()


def main():
    """Entry point for kraken_EURUSD_depth subscriber"""
    subscriber = KrakenEurusdDepthSubscriber()
    
    try:
        subscriber.run()
    except KeyboardInterrupt:
        logger.info("{subscriber.service_name} subscriber interrupted by user")
        subscriber.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"{subscriber.service_name} subscriber error: {e}", exc_info=True)
        subscriber.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
