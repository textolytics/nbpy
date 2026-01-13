"""
ZMQ Port Registry and Configuration

This module defines all ZMQ ports and their mappings for the nbpy microservices.
All ports are centrally managed here to ensure uniqueness and prevent conflicts.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PortConfig:
    """Configuration for a ZMQ service port"""
    port: int
    service_name: str
    service_type: str  # 'PUB', 'SUB', 'REP', 'REQ', etc.
    description: str
    topic_filter: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'port': self.port,
            'service_name': self.service_name,
            'service_type': self.service_type,
            'description': self.description,
            'topic_filter': self.topic_filter,
        }


# Define all ZMQ service ports
# OANDA Publishers
OANDA_PUB = PortConfig(
    port=5556,
    service_name='oanda_publisher',
    service_type='PUB',
    description='OANDA data publisher',
    topic_filter='oanda'
)

# Kraken Publishers
KRAKEN_TICK_PUB = PortConfig(
    port=5558,
    service_name='kraken_tick_publisher',
    service_type='PUB',
    description='Kraken ticker data publisher',
    topic_filter='kraken_tick'
)

KRAKEN_EURUSD_TICK_PUB = PortConfig(
    port=5559,
    service_name='kraken_eurusd_tick_publisher',
    service_type='PUB',
    description='Kraken EUR/USD specific ticker publisher',
    topic_filter='kr_eurusd_tick'
)

KRAKEN_DEPTH_PUB = PortConfig(
    port=5560,
    service_name='kraken_depth_publisher',
    service_type='PUB',
    description='Kraken order book depth publisher',
    topic_filter='kr_depth'
)

KRAKEN_ORDERS_PUB = PortConfig(
    port=5561,
    service_name='kraken_orders_publisher',
    service_type='PUB',
    description='Kraken orders/trades publisher',
    topic_filter='kraken_orders'
)

KRAKEN_EURUSD_DEPTH_PUB = PortConfig(
    port=5566,
    service_name='kraken_eurusd_depth_publisher',
    service_type='PUB',
    description='Kraken EUR/USD order book publisher',
    topic_filter='kr_eurusd_depth'
)

# OANDA Advanced Publishers
OANDA_TICK_PUB = PortConfig(
    port=5562,
    service_name='oanda_tick_publisher',
    service_type='PUB',
    description='OANDA ticker data publisher',
    topic_filter='oanda_tick'
)

OANDA_ORDERS_PUB = PortConfig(
    port=5563,
    service_name='oanda_orders_publisher',
    service_type='PUB',
    description='OANDA orders publisher',
    topic_filter='oanda_orders'
)

OANDAV20_TICK_PUB = PortConfig(
    port=5567,
    service_name='oandav20_tick_publisher',
    service_type='PUB',
    description='OANDA v20 API ticker publisher',
    topic_filter='oandav20_tick'
)

# Other Streams
BETFAIR_STREAM_PUB = PortConfig(
    port=5564,
    service_name='betfair_stream_publisher',
    service_type='PUB',
    description='Betfair streaming data publisher',
    topic_filter='betfair_stream'
)

TWITTER_SENTIMENT_PUB = PortConfig(
    port=5565,
    service_name='twitter_sentiment_publisher',
    service_type='PUB',
    description='Twitter sentiment data publisher',
    topic_filter='twitter_sentiment'
)

# Subscribers
KRAKEN_INFLUXDB_TICK_SUB = PortConfig(
    port=5578,
    service_name='kraken_influxdb_tick_subscriber',
    service_type='SUB',
    description='Kraken tick data subscriber to InfluxDB',
    topic_filter='kraken_tick'
)

KRAKEN_INFLUXDB_DEPTH_SUB = PortConfig(
    port=5579,
    service_name='kraken_influxdb_depth_subscriber',
    service_type='SUB',
    description='Kraken depth data subscriber to InfluxDB',
    topic_filter='kraken_depth'
)

KRAKEN_PGSQL_TICK_SUB = PortConfig(
    port=5580,
    service_name='kraken_pgsql_tick_subscriber',
    service_type='SUB',
    description='Kraken tick data subscriber to PostgreSQL',
    topic_filter='kraken_tick'
)

OANDA_INFLUXDB_TICK_SUB = PortConfig(
    port=5581,
    service_name='oanda_influxdb_tick_subscriber',
    service_type='SUB',
    description='OANDA tick data subscriber to InfluxDB',
    topic_filter='oanda_tick'
)

OANDA_PGSQL_TICK_SUB = PortConfig(
    port=5582,
    service_name='oanda_pgsql_tick_subscriber',
    service_type='SUB',
    description='OANDA tick data subscriber to PostgreSQL',
    topic_filter='oanda_tick'
)

TWITTER_INFLUXDB_SUB = PortConfig(
    port=5583,
    service_name='twitter_influxdb_subscriber',
    service_type='SUB',
    description='Twitter sentiment subscriber to InfluxDB',
    topic_filter='twitter_sentiment'
)

TWITTER_PGSQL_SUB = PortConfig(
    port=5584,
    service_name='twitter_pgsql_subscriber',
    service_type='SUB',
    description='Twitter sentiment subscriber to PostgreSQL',
    topic_filter='twitter_sentiment'
)

# Port registry
PORT_REGISTRY: Dict[str, PortConfig] = {
    # Publishers
    'oanda_pub': OANDA_PUB,
    'kraken_tick_pub': KRAKEN_TICK_PUB,
    'kraken_eurusd_tick_pub': KRAKEN_EURUSD_TICK_PUB,
    'kraken_depth_pub': KRAKEN_DEPTH_PUB,
    'kraken_orders_pub': KRAKEN_ORDERS_PUB,
    'kraken_eurusd_depth_pub': KRAKEN_EURUSD_DEPTH_PUB,
    'oanda_tick_pub': OANDA_TICK_PUB,
    'oanda_orders_pub': OANDA_ORDERS_PUB,
    'oandav20_tick_pub': OANDAV20_TICK_PUB,
    'betfair_stream_pub': BETFAIR_STREAM_PUB,
    'twitter_sentiment_pub': TWITTER_SENTIMENT_PUB,
    
    # Subscribers
    'kraken_influxdb_tick_sub': KRAKEN_INFLUXDB_TICK_SUB,
    'kraken_influxdb_depth_sub': KRAKEN_INFLUXDB_DEPTH_SUB,
    'kraken_pgsql_tick_sub': KRAKEN_PGSQL_TICK_SUB,
    'oanda_influxdb_tick_sub': OANDA_INFLUXDB_TICK_SUB,
    'oanda_pgsql_tick_sub': OANDA_PGSQL_TICK_SUB,
    'twitter_influxdb_sub': TWITTER_INFLUXDB_SUB,
    'twitter_pgsql_sub': TWITTER_PGSQL_SUB,
}


def get_port_config(service_name: str) -> Optional[PortConfig]:
    """Get port configuration for a service by name"""
    return PORT_REGISTRY.get(service_name.lower())


def get_port(service_name: str) -> Optional[int]:
    """Get port number for a service by name"""
    config = get_port_config(service_name)
    return config.port if config else None


def list_ports() -> Dict[str, PortConfig]:
    """List all registered ports"""
    return PORT_REGISTRY.copy()


def validate_port_uniqueness() -> bool:
    """Validate that all registered ports are unique"""
    ports = [config.port for config in PORT_REGISTRY.values()]
    return len(ports) == len(set(ports))


def get_ports_by_type(service_type: str) -> Dict[str, PortConfig]:
    """Get all ports of a specific type (PUB, SUB, etc.)"""
    return {
        name: config 
        for name, config in PORT_REGISTRY.items() 
        if config.service_type == service_type
    }
