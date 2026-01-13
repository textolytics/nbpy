#!/usr/bin/env python3
"""
NBPY ZMQ Microservices - Usage Examples

This file contains practical examples of how to use the nbpy.zmq module
for publishing and subscribing to market data.
"""

import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Publisher using BasePublisher
# ============================================================================

def example_1_basic_publisher():
    """
    Example 1: Create a basic publisher using BasePublisher
    
    This is the simplest way to publish data to a ZMQ topic.
    """
    from nbpy.zmq import BasePublisher, KRAKEN_TICK_PUB
    
    # Create publisher for Kraken tick data
    publisher = BasePublisher(KRAKEN_TICK_PUB)
    
    logger.info("Starting basic publisher example...")
    
    try:
        for i in range(5):
            data = {
                'timestamp': time.time(),
                'instrument': 'EURUSD',
                'bid': 1.08234 + i * 0.001,
                'ask': 1.08245 + i * 0.001,
                'volume': 1000000 + i * 100000
            }
            
            # Publish as JSON (automatically converted to MessagePack)
            publisher.publish_json(KRAKEN_TICK_PUB.topic_filter, data)
            logger.info(f"Published: {data}")
            
            time.sleep(1)
    
    finally:
        publisher.cleanup()


# ============================================================================
# EXAMPLE 2: Basic Subscriber using BaseSubscriber
# ============================================================================

def example_2_basic_subscriber():
    """
    Example 2: Create a basic subscriber using BaseSubscriber
    
    This receives and processes messages from a publisher.
    """
    from nbpy.zmq import BaseSubscriber, KRAKEN_TICK_PUB
    
    # Create subscriber
    subscriber = BaseSubscriber(KRAKEN_TICK_PUB, host='localhost')
    
    logger.info("Starting basic subscriber example...")
    logger.info("Listening for messages (press Ctrl+C to stop)...")
    
    try:
        for i in range(5):
            topic, data = subscriber.recv_msgpack()
            logger.info(f"Received: {topic} = {data}")
    
    except KeyboardInterrupt:
        logger.info("Subscriber stopped by user")
    finally:
        subscriber.cleanup()


# ============================================================================
# EXAMPLE 3: Custom Publisher with Data Source
# ============================================================================

def example_3_custom_publisher():
    """
    Example 3: Create a custom publisher with real data source
    
    This demonstrates how to create a publisher that fetches data
    from a real source (simulated here).
    """
    from nbpy.zmq import BasePublisher, PortConfig
    import random
    
    # Define custom port configuration
    custom_config = PortConfig(
        port=5600,
        service_name='custom_publisher',
        service_type='PUB',
        description='Custom market data publisher',
        topic_filter='custom_prices'
    )
    
    class CustomDataPublisher(BasePublisher):
        """Publisher that simulates market data"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.prices = {
                'EURUSD': 1.08234,
                'GBPUSD': 1.27456,
                'USDJPY': 149.234
            }
        
        def fetch_prices(self) -> Dict[str, Any]:
            """Fetch latest prices (simulated)"""
            # Simulate price movement
            for instrument in self.prices:
                self.prices[instrument] += random.uniform(-0.001, 0.001)
            
            return {
                'timestamp': time.time(),
                'prices': self.prices,
                'source': 'custom_feed'
            }
        
        def run(self, interval: float = 1.0):
            """Run publisher loop"""
            self.running = True
            count = 0
            
            try:
                while self.running and count < 5:
                    prices = self.fetch_prices()
                    self.publish_json(self.port_config.topic_filter, prices)
                    logger.info(f"Published prices: {prices}")
                    time.sleep(interval)
                    count += 1
            
            finally:
                self.cleanup()
    
    # Create and run publisher
    publisher = CustomDataPublisher(custom_config)
    publisher.run(interval=2.0)


# ============================================================================
# EXAMPLE 4: Custom Subscriber with Data Processing
# ============================================================================

def example_4_custom_subscriber():
    """
    Example 4: Create a custom subscriber with data processing
    
    This demonstrates how to create a subscriber that processes
    received messages before storing them.
    """
    from nbpy.zmq import BaseSubscriber, PortConfig
    
    config = PortConfig(
        port=5600,
        service_name='custom_subscriber',
        service_type='SUB',
        description='Custom price processor',
        topic_filter='custom_prices'
    )
    
    class PriceProcessor(BaseSubscriber):
        """Subscriber that processes and logs prices"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.stats = {
                'messages_received': 0,
                'instruments_seen': set(),
                'min_price': float('inf'),
                'max_price': float('-inf')
            }
        
        def process_message(self, topic: str, data: Dict[str, Any]):
            """Process received message"""
            self.stats['messages_received'] += 1
            
            prices = data.get('prices', {})
            for instrument, price in prices.items():
                self.stats['instruments_seen'].add(instrument)
                self.stats['min_price'] = min(self.stats['min_price'], price)
                self.stats['max_price'] = max(self.stats['max_price'], price)
                
                logger.info(f"{instrument}: {price:.5f}")
            
            # Print stats every 5 messages
            if self.stats['messages_received'] % 5 == 0:
                logger.info(f"Stats: {self.stats}")
        
        def run(self, max_messages: int = 5):
            """Run subscriber for limited messages"""
            self.running = True
            
            try:
                while self.running and self.stats['messages_received'] < max_messages:
                    topic, data = self.recv_msgpack()
                    self.process_message(topic, data)
            
            finally:
                logger.info(f"Final stats: {self.stats}")
                self.cleanup()
    
    # This would need a publisher running on port 5600
    logger.info("Custom subscriber example requires publisher on port 5600")


# ============================================================================
# EXAMPLE 5: Using the Kraken Tick Publisher
# ============================================================================

def example_5_kraken_tick_publisher():
    """
    Example 5: Use the built-in KrakenTickPublisher
    
    This publishes real Kraken ticker data.
    """
    from nbpy.zmq.publishers.kraken_tick import KrakenTickPublisher
    
    logger.info("Starting Kraken tick publisher...")
    logger.info("This requires the 'ccs' library for Kraken API access")
    
    try:
        publisher = KrakenTickPublisher()
        logger.info(f"Publisher initialized with {len(publisher.instruments)} instruments")
        
        # Run for a short time
        publisher.running = True
        start_time = time.time()
        
        while time.time() - start_time < 10:
            # The run() method would normally loop forever
            # For this example, we'll just show the setup
            logger.info(f"Publisher ready on port {publisher.port_config.port}")
            break
        
        publisher.cleanup()
    
    except Exception as e:
        logger.error(f"Could not start Kraken publisher: {e}")


# ============================================================================
# EXAMPLE 6: Pub/Sub Pattern with Multiple Topics
# ============================================================================

def example_6_multiple_topics():
    """
    Example 6: Demonstrate pub/sub with filtering by topic
    
    This shows how to subscribe to specific topics only.
    """
    from nbpy.zmq import PortConfig, BasePublisher, BaseSubscriber
    import threading
    
    logger.info("Starting multi-topic example...")
    
    # Define custom configs for multiple topics
    tick_config = PortConfig(
        port=5700,
        service_name='tick_feed',
        service_type='PUB',
        description='Tick feed',
        topic_filter='ticks'
    )
    
    depth_config = PortConfig(
        port=5701,
        service_name='depth_feed',
        service_type='PUB',
        description='Depth feed',
        topic_filter='depth'
    )
    
    # This demonstrates the concept - actual implementation would
    # require running publishers separately
    logger.info(f"Tick topic on port {tick_config.port}")
    logger.info(f"Depth topic on port {depth_config.port}")
    logger.info("Subscribers would connect to specific ports based on interest")


# ============================================================================
# EXAMPLE 7: Using Port Registry
# ============================================================================

def example_7_port_registry():
    """
    Example 7: Access the port registry for service discovery
    
    This shows how to programmatically discover available services.
    """
    from nbpy.zmq import (
        list_ports,
        get_port_config,
        get_ports_by_type,
        validate_port_uniqueness
    )
    
    logger.info("=== Port Registry Discovery ===")
    
    # List all ports
    all_ports = list_ports()
    logger.info(f"Total registered services: {len(all_ports)}")
    
    # Get specific service
    kraken_config = get_port_config('kraken_tick_pub')
    if kraken_config:
        logger.info(f"Kraken Tick Publisher: {kraken_config.description}")
        logger.info(f"  Port: {kraken_config.port}")
        logger.info(f"  Topic: {kraken_config.topic_filter}")
    
    # List by type
    publishers = get_ports_by_type('PUB')
    subscribers = get_ports_by_type('SUB')
    logger.info(f"Publishers: {len(publishers)}, Subscribers: {len(subscribers)}")
    
    # Validate
    is_valid = validate_port_uniqueness()
    logger.info(f"Port uniqueness valid: {is_valid}")


# ============================================================================
# EXAMPLE 8: Message Serialization
# ============================================================================

def example_8_serialization():
    """
    Example 8: Demonstrate MessagePack serialization
    
    Shows how to serialize and deserialize messages.
    """
    from nbpy.zmq.serialization import (
        MessagePackCodec,
        ZMQMessageHandler,
        convert_json_to_msgpack,
        convert_msgpack_to_json
    )
    
    logger.info("=== MessagePack Serialization ===")
    
    # Sample data
    data = {
        'instrument': 'EURUSD',
        'bid': 1.08234,
        'ask': 1.08245,
        'timestamp': 1234567890,
        'nested': {
            'level2': {
                'value': 42
            }
        }
    }
    
    # Pack individual data
    packed = MessagePackCodec.pack(data)
    logger.info(f"Original JSON: {len(str(data))} chars")
    logger.info(f"MessagePack: {len(packed)} bytes")
    logger.info(f"Compression: {100 * len(packed) / len(str(data)):.1f}%")
    
    # Unpack
    unpacked = MessagePackCodec.unpack(packed)
    logger.info(f"Data preserved: {unpacked == data}")
    
    # Multipart messages
    message = ZMQMessageHandler.serialize_multipart('test_topic', data)
    logger.info(f"Multipart message parts: {len(message)}")
    logger.info(f"  Topic: {len(message[0])} bytes")
    logger.info(f"  Data: {len(message[1])} bytes")
    
    topic, recovered = ZMQMessageHandler.deserialize_multipart(message)
    logger.info(f"Recovered topic: {topic}")
    logger.info(f"Data matches: {recovered == data}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run all examples"""
    examples = [
        ("Port Registry", example_7_port_registry),
        ("Serialization", example_8_serialization),
        # Uncomment below to run interactive examples
        # ("Basic Publisher", example_1_basic_publisher),
        # ("Kraken Publisher", example_5_kraken_tick_publisher),
    ]
    
    logger.info("=" * 70)
    logger.info("NBPY ZMQ MICROSERVICES - USAGE EXAMPLES")
    logger.info("=" * 70)
    
    for example_name, example_func in examples:
        logger.info(f"\n>>> Running: {example_name}")
        logger.info("-" * 70)
        
        try:
            example_func()
        except Exception as e:
            logger.error(f"Example failed: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("-" * 70)
    
    logger.info("\n" + "=" * 70)
    logger.info("Examples complete!")
    logger.info("=" * 70)
    logger.info("\nTo run interactive examples:")
    logger.info("  1. Uncomment example functions in main()")
    logger.info("  2. Run publisher and subscriber in separate terminals")
    logger.info("  3. Use: nbpy-pub-kraken-tick & nbpy-sub-kraken-influxdb-tick")


if __name__ == '__main__':
    main()
