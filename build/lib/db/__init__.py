"""
nbpy.db - Database module for nbpy project

This package provides database services and utilities for the nbpy project,
including InfluxDB integration for time-series data storage and ZMQ integration.

Submodules:
    influxdb_service: Core InfluxDB service and data models
    config: Configuration management
    zmq_influxdb_bridge: ZMQ to InfluxDB integration
"""

from .influxdb_service import (
    InfluxDBService,
    InfluxDBConfig,
    BaseDataPoint,
    TickData,
    DepthData,
    OHLCData,
    SentimentData,
    DataType,
    create_service,
    parse_kraken_tick_message,
    parse_oanda_tick_message,
)

from .config import (
    InfluxDBEnvironmentConfig,
    InfluxDBConfigFile,
    ServiceConfigBuilder,
    ConfigManager,
    get_config_manager,
)

from .zmq_influxdb_bridge import (
    ZMQInfluxDBBridge,
    KrakenTickBridge,
    OandaTickBridge,
    GenericZMQBridge,
    create_kraken_bridge,
    create_oanda_bridge,
    create_generic_bridge,
)

__version__ = "1.0.0"
__all__ = [
    # Core InfluxDB service
    "InfluxDBService",
    "InfluxDBConfig",
    "BaseDataPoint",
    "TickData",
    "DepthData",
    "OHLCData",
    "SentimentData",
    "DataType",
    "create_service",
    "parse_kraken_tick_message",
    "parse_oanda_tick_message",
    # Configuration
    "InfluxDBEnvironmentConfig",
    "InfluxDBConfigFile",
    "ServiceConfigBuilder",
    "ConfigManager",
    "get_config_manager",
    # ZMQ Bridges
    "ZMQInfluxDBBridge",
    "KrakenTickBridge",
    "OandaTickBridge",
    "GenericZMQBridge",
    "create_kraken_bridge",
    "create_oanda_bridge",
    "create_generic_bridge",
]
