"""
nbpy_zmq: ZMQ-based market data ETL and analytics framework

This package provides publishers, subscribers, and forwarders for:
- Forex data (Oanda API)
- Cryptocurrency data (Kraken API)
- Twitter sentiment analysis
- Cross-rate arbitrage calculations
- Time-series persistence (InfluxDB, PostgreSQL)
"""

__version__ = "0.1.0"
__author__ = "nbpy developers"

from .utils.config import ZMQConfig
from .utils.message_bus import MessageBus

__all__ = ["ZMQConfig", "MessageBus"]
