"""ZMQ configuration management."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ZMQConfig:
    """Configuration for ZMQ message bus."""
    
    # Network settings
    host: str = "localhost"
    pub_port: int = 5559
    sub_port: int = 5560
    
    # Kraken API settings
    kraken_host: Optional[str] = "api.kraken.com"
    kraken_order_book_depth: int = 1
    
    # Oanda API settings
    oanda_practice_host: str = "stream-fxpractice.oanda.com"
    oanda_live_host: str = "stream-fxtrade.oanda.com"
    
    # InfluxDB settings
    influxdb_host: str = "192.168.0.33"
    influxdb_port: int = 8086
    influxdb_user: str = "zmq"
    influxdb_password: str = "zmq"
    influxdb_db: str = "tick"
    
    # Message settings
    message_batch_size: int = 500
    message_time_precision: str = "ms"
    
    # Default topics
    default_kraken_tick_topic: str = "kr_eurusd_tick"
    default_kraken_depth_topic: str = "kr_depth"
    default_oanda_tick_topic: str = "oanda_tick"
    default_twitter_sentiment_topic: str = "twitter_sentiment"
    
    def get_zmq_url(self, port: Optional[int] = None, host: Optional[str] = None) -> str:
        """Generate ZMQ connection URL."""
        _host = host or self.host
        _port = port or self.pub_port
        return f"tcp://{_host}:{_port}"
    
    def get_influxdb_url(self) -> str:
        """Generate InfluxDB connection URL."""
        return f"http://{self.influxdb_host}:{self.influxdb_port}"
