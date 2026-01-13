#!/usr/bin/env python3
"""
ZMQ Microservices Validation and Integration Tests

Validates the migration of zmq services to the nbpy module with:
- Port registry validation
- MessagePack serialization tests
- ZMQ pub/sub pattern validation
- Import tests
"""

import sys
import logging
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports() -> bool:
    """Test that all modules import correctly"""
    logger.info("Testing imports...")
    try:
        from nbpy.zmq import (
            PortConfig,
            PORT_REGISTRY,
            get_port_config,
            get_port,
            validate_port_uniqueness,
            MessagePackCodec,
            ZMQMessageHandler,
            BasePublisher,
            BaseSubscriber,
            KRAKEN_TICK_PUB,
        )
        logger.info("✓ All core modules imported successfully")
        
        from nbpy.zmq.publishers import kraken_tick
        logger.info("✓ Publisher modules imported successfully")
        
        from nbpy.zmq.subscribers import influxdb_tick
        logger.info("✓ Subscriber modules imported successfully")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_port_registry() -> bool:
    """Test port registry and validation"""
    logger.info("\nTesting port registry...")
    try:
        from nbpy.zmq import (
            PORT_REGISTRY,
            validate_port_uniqueness,
            get_port_config,
            get_ports_by_type,
        )
        
        # Check port uniqueness
        if not validate_port_uniqueness():
            logger.error("✗ Port uniqueness validation failed")
            return False
        logger.info("✓ All ports are unique")
        
        # List all ports
        print("\nRegistered Ports:")
        print("-" * 80)
        for name, config in PORT_REGISTRY.items():
            print(f"  {name:30} Port: {config.port:5} Type: {config.service_type:5} Topic: {config.topic_filter}")
        
        # Test port lookup
        config = get_port_config('kraken_tick_pub')
        if config is None or config.port != 5558:
            logger.error("✗ Port config lookup failed")
            return False
        logger.info("✓ Port configuration lookup working")
        
        # Test filter by type
        pub_ports = get_ports_by_type('PUB')
        sub_ports = get_ports_by_type('SUB')
        logger.info(f"✓ Found {len(pub_ports)} PUB ports and {len(sub_ports)} SUB ports")
        
        return True
    except Exception as e:
        logger.error(f"✗ Port registry test failed: {e}")
        return False


def test_messagepack_serialization() -> bool:
    """Test MessagePack serialization"""
    logger.info("\nTesting MessagePack serialization...")
    try:
        from nbpy.zmq.serialization import (
            MessagePackCodec,
            ZMQMessageHandler,
            convert_json_to_msgpack,
            convert_msgpack_to_json,
        )
        
        # Test data
        test_data = {
            'instrument': 'EURUSD',
            'bid': 1.08234,
            'ask': 1.08245,
            'timestamp': 1234567890,
            'nested': {'value': 42}
        }
        
        # Test MessagePack codec
        packed = MessagePackCodec.pack(test_data)
        if not isinstance(packed, bytes):
            logger.error("✗ Pack should return bytes")
            return False
        logger.info(f"✓ Packed {len(test_data)} fields to {len(packed)} bytes")
        
        unpacked = MessagePackCodec.unpack(packed)
        if unpacked != test_data:
            logger.error(f"✗ Unpack mismatch: {unpacked} != {test_data}")
            return False
        logger.info("✓ Unpack matches original data")
        
        # Test message handler
        message_parts = ZMQMessageHandler.serialize_multipart('test_topic', test_data)
        if len(message_parts) != 2:
            logger.error(f"✗ Expected 2 message parts, got {len(message_parts)}")
            return False
        logger.info(f"✓ Serialized multipart message ({len(message_parts[0])} + {len(message_parts[1])} bytes)")
        
        topic, data = ZMQMessageHandler.deserialize_multipart(message_parts)
        if topic != 'test_topic' or data != test_data:
            logger.error(f"✗ Deserialization mismatch")
            return False
        logger.info("✓ Deserialized multipart message correctly")
        
        # Test JSON conversion
        json_packed = convert_json_to_msgpack(test_data)
        json_unpacked = convert_msgpack_to_json(json_packed)
        if json_unpacked != test_data:
            logger.error(f"✗ JSON conversion failed")
            return False
        logger.info("✓ JSON to MessagePack conversion working")
        
        return True
    except Exception as e:
        logger.error(f"✗ MessagePack serialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_classes() -> bool:
    """Test base publisher and subscriber classes"""
    logger.info("\nTesting base ZMQ classes...")
    try:
        from nbpy.zmq import BasePublisher, BaseSubscriber, KRAKEN_TICK_PUB
        
        # Test publisher instantiation
        pub = BasePublisher(KRAKEN_TICK_PUB)
        logger.info(f"✓ Publisher instantiated on port {KRAKEN_TICK_PUB.port}")
        pub.cleanup()
        
        # Test subscriber instantiation (won't connect without publisher running)
        # sub = BaseSubscriber(KRAKEN_TICK_PUB, host='localhost')
        # logger.info(f"✓ Subscriber instantiated")
        # sub.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"✗ Base class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_publisher_classes() -> bool:
    """Test publisher implementations"""
    logger.info("\nTesting publisher implementations...")
    try:
        from nbpy.zmq.publishers.kraken_tick import KrakenTickPublisher
        
        publisher = KrakenTickPublisher()
        logger.info(f"✓ KrakenTickPublisher instantiated on port {publisher.port_config.port}")
        logger.info(f"  - Topic filter: {publisher.port_config.topic_filter}")
        logger.info(f"  - Instruments: {publisher.instruments[:5] if len(publisher.instruments) >= 5 else publisher.instruments}")
        publisher.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"✗ Publisher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subscriber_classes() -> bool:
    """Test subscriber implementations"""
    logger.info("\nTesting subscriber implementations...")
    try:
        from nbpy.zmq.subscribers.influxdb_tick import KrakenTickToInfluxDBSubscriber
        
        # Test instantiation (won't actually connect)
        subscriber = KrakenTickToInfluxDBSubscriber()
        logger.info(f"✓ KrakenTickToInfluxDBSubscriber instantiated")
        logger.info(f"  - ZMQ Host: {subscriber.host}")
        logger.info(f"  - InfluxDB: {subscriber.influxdb_host}:{subscriber.influxdb_port}/{subscriber.influxdb_db}")
        logger.info(f"  - Topic filter: {subscriber.port_config.topic_filter}")
        subscriber.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"✗ Subscriber test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests() -> bool:
    """Run all validation tests"""
    logger.info("=" * 80)
    logger.info("NBPY ZMQ MICROSERVICES VALIDATION")
    logger.info("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("Port Registry", test_port_registry),
        ("MessagePack Serialization", test_messagepack_serialization),
        ("Base ZMQ Classes", test_base_classes),
        ("Publisher Classes", test_publisher_classes),
        ("Subscriber Classes", test_subscriber_classes),
    ]
    
    results: Dict[str, bool] = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("-" * 80)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 80)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
