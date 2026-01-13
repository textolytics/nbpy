"""
nbpy.zmq - ZMQ Microservices Module

This module provides a complete ZMQ pub/sub microservices framework for nbpy,
with MessagePack serialization, centralized port management, and comprehensive
logging and error handling.

Submodules:
    ports: Port registry and configuration management
    serialization: MessagePack serialization/deserialization
    base: Base classes for PUB and SUB services
    publishers: Publisher microservices for various data sources
    subscribers: Subscriber microservices for various backends
"""

import logging

from .ports import (
    PortConfig,
    PORT_REGISTRY,
    get_port_config,
    get_port,
    list_ports,
    validate_port_uniqueness,
    get_ports_by_type,
    # Specific port configs
    KRAKEN_TICK_PUB,
    KRAKEN_DEPTH_PUB,
    KRAKEN_ORDERS_PUB,
    KRAKEN_EURUSD_TICK_PUB,
    OANDA_TICK_PUB,
    OANDA_ORDERS_PUB,
    BETFAIR_STREAM_PUB,
    TWITTER_SENTIMENT_PUB,
    KRAKEN_INFLUXDB_TICK_SUB,
)

from .serialization import (
    MessagePackCodec,
    ZMQMessageHandler,
    convert_json_to_msgpack,
    convert_msgpack_to_json,
)

from .base import (
    BaseZMQService,
    BasePublisher,
    BaseSubscriber,
)

__version__ = "1.0.0"

__all__ = [
    # Port management
    "PortConfig",
    "PORT_REGISTRY",
    "get_port_config",
    "get_port",
    "list_ports",
    "validate_port_uniqueness",
    "get_ports_by_type",
    # Specific ports
    "KRAKEN_TICK_PUB",
    "KRAKEN_DEPTH_PUB",
    "KRAKEN_ORDERS_PUB",
    "KRAKEN_EURUSD_TICK_PUB",
    "OANDA_TICK_PUB",
    "OANDA_ORDERS_PUB",
    "BETFAIR_STREAM_PUB",
    "TWITTER_SENTIMENT_PUB",
    "KRAKEN_INFLUXDB_TICK_SUB",
    # Serialization
    "MessagePackCodec",
    "ZMQMessageHandler",
    "convert_json_to_msgpack",
    "convert_msgpack_to_json",
    # Base classes
    "BaseZMQService",
    "BasePublisher",
    "BaseSubscriber",
]

# Configure logging for this module
logger = logging.getLogger(__name__)


def validate_configuration() -> bool:
    """
    Validate ZMQ configuration
    
    Returns:
        True if configuration is valid
    """
    if not validate_port_uniqueness():
        logger.error("Port uniqueness validation failed!")
        return False
    
    logger.info("ZMQ configuration validated successfully")
    return True
