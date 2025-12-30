"""Example: Simple Kraken tick publisher."""

import logging
import time
import json
from nbpy_zmq.utils import ZMQConfig, MessageBus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Publish mock Kraken tick data."""
    config = ZMQConfig()
    bus = MessageBus(config)
    
    # Create publisher
    pub_socket = bus.create_publisher(port=config.pub_port)
    
    logger.info("Publishing Kraken EURUSD ticks...")
    
    # Mock data
    ticks = [
        {"instrument": "EUR_USD", "bid": 1.0820, "ask": 1.0825},
        {"instrument": "EUR_USD", "bid": 1.0821, "ask": 1.0826},
        {"instrument": "EUR_USD", "bid": 1.0819, "ask": 1.0824},
    ]
    
    try:
        for tick in ticks:
            # Format as tab-separated values
            message_data = "\x01".join([
                tick["instrument"],
                str(tick["bid"]),
                str(tick["ask"]),
            ])
            
            bus.send_message("kr_eurusd_tick", message_data)
            logger.info(f"Published: {tick}")
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Publisher interrupted")
    finally:
        bus.close()


if __name__ == "__main__":
    main()
