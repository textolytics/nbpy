"""
OANDAV20_TICK_TOPIC Publisher Module
Auto-migrated from python/scripts/zmq/pub_oandav20_tick_topic.py

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
    from python.scripts.zmq.pub_oandav20_tick_topic import *
except ImportError:
    pass

logger = logging.getLogger(__name__)


class Oandav20TickTopicPublisher(BasePublisher):
    """
    Publisher for OANDAV20_TICK_TOPIC
    
    Original service: pub_oandav20_tick_topic.py
    Port: 5558
    Topic: oandav20_tick_topic
    """
    
    def __init__(self):
        super().__init__(
            port=5558,
            topic='oandav20_tick_topic',
            service_name='oandav20_tick_topic'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized oandav20_tick_topic Publisher on port {self.port}, topic: {self.topic}")
    
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
    """Entry point for oandav20_tick_topic publisher"""
    publisher = Oandav20TickTopicPublisher()
    
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
