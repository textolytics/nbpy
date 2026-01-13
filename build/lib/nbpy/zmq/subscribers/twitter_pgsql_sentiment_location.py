"""
TWITTER_PGSQL_SENTIMENT_LOCATION Subscriber Module
Auto-migrated from python/scripts/zmq/sub_twitter_pgsql_sentiment_location.py

This module wraps the original implementation while providing
nbpy.zmq framework integration with MessagePack deserialization.
"""

import sys
import logging
from pathlib import Path

# Import framework components
from nbpy.zmq.base import BaseSubscriber, BasePostgreSQLSubscriber
from nbpy.zmq.ports import PORT_REGISTRY
from nbpy.zmq.serialization import MessagePackCodec

logger = logging.getLogger(__name__)


class TwitterPgsqlSentimentLocationSubscriber(BasePostgreSQLSubscriber):
    """
    Subscriber for TWITTER_PGSQL_SENTIMENT_LOCATION
    
    Original service: sub_twitter_pgsql_sentiment_location.py
    Connection port: 5558
    Topic filter: twitter_pgsql_sentiment_location
    Backend type: generic
    """
    
    def __init__(self, connection_port=5558, topic_filter='twitter_pgsql_sentiment_location'):
        super().__init__(
            connection_port=connection_port,
            topic_filter=topic_filter,
            service_name='twitter_pgsql_sentiment_location'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized twitter_pgsql_sentiment_location Subscriber on port {self.connection_port}, topic: {self.topic_filter}")
    
    def process_message(self, topic, data):
        """Process incoming message - implement service-specific logic"""
        try:
            # Deserialize MessagePack data
            message = self.codec.unpack(data)
            
            # Import and run original service logic
            from python.scripts.zmq.sub_twitter_pgsql_sentiment_location import process_message
            
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
            from python.scripts.zmq.sub_twitter_pgsql_sentiment_location import run
            
            run()
            
        except ImportError:
            logger.error(f"Could not import original module: sub_twitter_pgsql_sentiment_location")
            logger.info("Please ensure python/scripts/zmq/ is in your PYTHONPATH")
            # Fall back to base implementation
            super().run()


def main():
    """Entry point for twitter_pgsql_sentiment_location subscriber"""
    subscriber = TwitterPgsqlSentimentLocationSubscriber()
    
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
