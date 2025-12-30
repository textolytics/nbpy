"""Example: Simple subscriber that listens to Kraken ticks."""

import logging
from nbpy_zmq.utils import ZMQConfig, MessageBus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Subscribe to Kraken EURUSD ticks."""
    config = ZMQConfig()
    bus = MessageBus(config)
    
    # Create subscriber
    sub_socket = bus.create_subscriber(
        topics=["kr_eurusd_tick"],
        port=config.pub_port
    )
    
    logger.info("Listening for Kraken EURUSD ticks...")
    
    try:
        for i in range(5):
            topic, data = bus.receive_message()
            parts = data.split('\x01')
            logger.info(f"[{topic}] instrument={parts[0]}, bid={parts[1]}, ask={parts[2]}")
    
    except KeyboardInterrupt:
        logger.info("Subscriber interrupted")
    finally:
        bus.close()


if __name__ == "__main__":
    main()
