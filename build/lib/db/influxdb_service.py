#!/usr/bin/env python
"""
InfluxDB Service Module for nbpy ZMQ Data Pipeline

This module provides a unified interface for storing time-series data from various
ZMQ publisher/subscriber services into InfluxDB. It includes:
- Connection management
- Multiple data schema handlers (Tick, Depth, Orders, Sentiment)
- Batch writing capabilities
- Error handling and retry logic
- Configurable databases and retention policies
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import socket
import os

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataType(Enum):
    """Supported data types for InfluxDB storage"""
    TICK = "tick"
    DEPTH = "depth"
    ORDERS = "orders"
    SENTIMENT = "sentiment"
    TRADE = "trade"
    OHLC = "ohlc"


@dataclass
class InfluxDBConfig:
    """Configuration for InfluxDB connection"""
    host: str = os.environ.get('INFLUXDB_HOST', 'influxdb')
    port: int = int(os.environ.get('INFLUXDB_PORT', 8086))
    username: str = os.environ.get('INFLUXDB_USER', 'zmq')
    password: str = os.environ.get('INFLUXDB_PASSWORD', 'y61327061')
    database: str = os.environ.get('INFLUXDB_DB', 'tick')
    ssl: bool = os.environ.get('INFLUXDB_SSL', 'false').lower() == 'true'
    verify_ssl: bool = os.environ.get('INFLUXDB_VERIFY_SSL', 'true').lower() == 'true'
    timeout: int = int(os.environ.get('INFLUXDB_TIMEOUT', 10))
    batch_size: int = int(os.environ.get('INFLUXDB_BATCH_SIZE', 500))
    write_consistency: str = os.environ.get('INFLUXDB_CONSISTENCY', 'one')
    retention_policy: str = os.environ.get('INFLUXDB_RETENTION', 'autogen')


class BaseDataPoint(ABC):
    """Abstract base class for data points"""
    
    @abstractmethod
    def to_influx_json(self) -> Dict[str, Any]:
        """Convert to InfluxDB JSON format"""
        pass


@dataclass
class TickData(BaseDataPoint):
    """Market tick data point"""
    instrument: str
    bid: float
    ask: float
    timestamp: Optional[int] = None
    base_ccy: Optional[str] = None
    term_ccy: Optional[str] = None
    volume: Optional[float] = None
    vwap: Optional[float] = None
    
    def to_influx_json(self) -> Dict[str, Any]:
        """Convert to InfluxDB JSON format"""
        tags = {
            "instrument": self.instrument
        }
        
        if self.base_ccy:
            tags["base_ccy"] = self.base_ccy
        if self.term_ccy:
            tags["term_ccy"] = self.term_ccy
            
        fields = {
            "bid": self.bid,
            "ask": self.ask
        }
        
        if self.volume:
            fields["volume"] = self.volume
        if self.vwap:
            fields["vwap"] = self.vwap
            
        point = {
            "measurement": DataType.TICK.value,
            "tags": tags,
            "fields": fields
        }
        
        if self.timestamp:
            point["time"] = self.timestamp
            
        return point


@dataclass
class DepthData(BaseDataPoint):
    """Market depth (order book) data point"""
    instrument: str
    timestamp: Optional[int] = None
    bid_prices: Optional[List[float]] = None
    bid_volumes: Optional[List[float]] = None
    ask_prices: Optional[List[float]] = None
    ask_volumes: Optional[List[float]] = None
    base_ccy: Optional[str] = None
    term_ccy: Optional[str] = None
    
    def to_influx_json(self) -> Dict[str, Any]:
        """Convert to InfluxDB JSON format"""
        tags = {
            "instrument": self.instrument
        }
        
        if self.base_ccy:
            tags["base_ccy"] = self.base_ccy
        if self.term_ccy:
            tags["term_ccy"] = self.term_ccy
        
        fields = {}
        
        if self.bid_prices and self.bid_volumes:
            fields["bid_price_1"] = float(self.bid_prices[0]) if self.bid_prices else None
            fields["bid_volume_1"] = float(self.bid_volumes[0]) if self.bid_volumes else None
            if len(self.bid_prices) > 1:
                fields["bid_price_2"] = float(self.bid_prices[1])
                fields["bid_volume_2"] = float(self.bid_volumes[1])
        
        if self.ask_prices and self.ask_volumes:
            fields["ask_price_1"] = float(self.ask_prices[0]) if self.ask_prices else None
            fields["ask_volume_1"] = float(self.ask_volumes[0]) if self.ask_volumes else None
            if len(self.ask_prices) > 1:
                fields["ask_price_2"] = float(self.ask_prices[1])
                fields["ask_volume_2"] = float(self.ask_volumes[1])
        
        point = {
            "measurement": DataType.DEPTH.value,
            "tags": tags,
            "fields": fields
        }
        
        if self.timestamp:
            point["time"] = self.timestamp
            
        return point


@dataclass
class OHLCData(BaseDataPoint):
    """OHLC (candle) data point"""
    instrument: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: Optional[int] = None
    base_ccy: Optional[str] = None
    term_ccy: Optional[str] = None
    trades: Optional[int] = None
    
    def to_influx_json(self) -> Dict[str, Any]:
        """Convert to InfluxDB JSON format"""
        tags = {
            "instrument": self.instrument
        }
        
        if self.base_ccy:
            tags["base_ccy"] = self.base_ccy
        if self.term_ccy:
            tags["term_ccy"] = self.term_ccy
        
        fields = {
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": float(self.volume)
        }
        
        if self.trades:
            fields["trades"] = int(self.trades)
        
        point = {
            "measurement": DataType.OHLC.value,
            "tags": tags,
            "fields": fields
        }
        
        if self.timestamp:
            point["time"] = self.timestamp
            
        return point


@dataclass
class SentimentData(BaseDataPoint):
    """Sentiment analysis data point"""
    source: str
    instrument: str
    sentiment_score: float
    timestamp: Optional[int] = None
    text: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    
    def to_influx_json(self) -> Dict[str, Any]:
        """Convert to InfluxDB JSON format"""
        tags = {
            "source": self.source,
            "instrument": self.instrument
        }
        
        if self.location:
            tags["location"] = self.location
        if self.language:
            tags["language"] = self.language
        
        fields = {
            "sentiment_score": float(self.sentiment_score)
        }
        
        if self.text:
            fields["text"] = self.text
        
        point = {
            "measurement": DataType.SENTIMENT.value,
            "tags": tags,
            "fields": fields
        }
        
        if self.timestamp:
            point["time"] = self.timestamp
            
        return point


class InfluxDBService:
    """
    Main service class for managing InfluxDB connections and data storage.
    
    Provides:
    - Connection management with retry logic
    - Multiple data type handlers
    - Batch writing with configurable batch sizes
    - Database and retention policy management
    - Error handling and logging
    """
    
    def __init__(self, config: Optional[InfluxDBConfig] = None):
        """
        Initialize InfluxDB service.
        
        Args:
            config: InfluxDBConfig instance. If None, uses default/env configuration.
        """
        self.config = config or InfluxDBConfig()
        self.client: Optional[InfluxDBClient] = None
        self.batch_buffer: List[Dict[str, Any]] = []
        self.last_write_time = time.time()
        self.write_count = 0
        self.error_count = 0
        
        logger.info(f"Initializing InfluxDB Service: {self.config.host}:{self.config.port}")
        self._connect()
    
    def _connect(self) -> bool:
        """
        Establish connection to InfluxDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = InfluxDBClient(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                database=self.config.database,
                ssl=self.config.ssl,
                verify_ssl=self.config.verify_ssl,
                timeout=self.config.timeout
            )
            
            # Verify connection
            self.client.ping()
            logger.info(f"Connected to InfluxDB: {self.config.host}:{self.config.port}")
            
            # Ensure database exists
            self._ensure_database()
            
            return True
            
        except (InfluxDBServerError, socket.timeout) as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self.client = None
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            self.client = None
            return False
    
    def _ensure_database(self) -> bool:
        """
        Ensure the database exists, create if necessary.
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.client:
                return False
            
            databases = self.client.get_list_database()
            db_names = [db['name'] for db in databases]
            
            if self.config.database not in db_names:
                logger.info(f"Creating database: {self.config.database}")
                self.client.create_database(self.config.database)
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring database: {e}")
            return False
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to InfluxDB.
        
        Returns:
            bool: True if reconnection successful
        """
        logger.warning("Attempting to reconnect to InfluxDB...")
        self.client = None
        return self._connect()
    
    def write_point(self, data_point: Union[BaseDataPoint, Dict[str, Any]]) -> bool:
        """
        Write a single data point to the batch buffer.
        
        Args:
            data_point: Data point object or dict
            
        Returns:
            bool: True if added to buffer successfully
        """
        try:
            if isinstance(data_point, BaseDataPoint):
                json_point = data_point.to_influx_json()
            elif isinstance(data_point, dict):
                json_point = data_point
            else:
                logger.error(f"Invalid data point type: {type(data_point)}")
                return False
            
            self.batch_buffer.append(json_point)
            
            # Auto-flush if batch size exceeded
            if len(self.batch_buffer) >= self.config.batch_size:
                self.flush()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding point to buffer: {e}")
            self.error_count += 1
            return False
    
    def write_points(self, data_points: List[Union[BaseDataPoint, Dict[str, Any]]]) -> bool:
        """
        Write multiple data points.
        
        Args:
            data_points: List of data point objects or dicts
            
        Returns:
            bool: True if all points added successfully
        """
        success = True
        for point in data_points:
            if not self.write_point(point):
                success = False
        
        return success
    
    def flush(self, force: bool = False) -> bool:
        """
        Flush buffered points to InfluxDB.
        
        Args:
            force: Force flush even if buffer is not full
            
        Returns:
            bool: True if flush successful
        """
        if not self.batch_buffer:
            return True
        
        if not force and len(self.batch_buffer) < self.config.batch_size:
            # Check if enough time has passed since last write
            if time.time() - self.last_write_time < 5:
                return True
        
        try:
            if not self.client:
                logger.warning("No client connection, attempting reconnect...")
                if not self.reconnect():
                    logger.error("Failed to reconnect to InfluxDB")
                    return False
            
            logger.debug(f"Writing {len(self.batch_buffer)} points to InfluxDB")
            self.client.write_points(
                self.batch_buffer,
                batch_size=self.config.batch_size,
                time_precision='ms',
                consistency=self.config.write_consistency,
                retention_policy=self.config.retention_policy
            )
            
            self.write_count += len(self.batch_buffer)
            self.batch_buffer = []
            self.last_write_time = time.time()
            
            logger.info(f"Flushed {len(self.batch_buffer)} points. Total writes: {self.write_count}")
            return True
            
        except (InfluxDBServerError, socket.timeout) as e:
            logger.error(f"Connection error during flush: {e}")
            self.error_count += 1
            if not self.reconnect():
                logger.error("Failed to reconnect after flush error")
                return False
            return self.flush(force=force)
            
        except Exception as e:
            logger.error(f"Error flushing points: {e}")
            self.error_count += 1
            return False
    
    def query(self, query_str: str) -> Optional[List[Dict]]:
        """
        Execute a query on InfluxDB.
        
        Args:
            query_str: InfluxDB query string
            
        Returns:
            Query results or None if error
        """
        try:
            if not self.client:
                return None
            
            result = self.client.query(query_str)
            return list(result.get_points())
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            return None
    
    def get_latest_tick(self, instrument: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest tick data for an instrument.
        
        Args:
            instrument: Instrument name (e.g., 'EURUSD')
            
        Returns:
            Latest tick data or None
        """
        query_str = f'SELECT * FROM "tick" WHERE "instrument"=\'{instrument}\' ORDER BY DESC LIMIT 1'
        results = self.query(query_str)
        return results[0] if results else None
    
    def get_ohlc(self, instrument: str, hours: int = 24) -> Optional[List[Dict[str, Any]]]:
        """
        Get OHLC data for the last N hours.
        
        Args:
            instrument: Instrument name
            hours: Number of hours to retrieve
            
        Returns:
            List of OHLC data points
        """
        query_str = (
            f'SELECT * FROM "ohlc" WHERE "instrument"=\'{instrument}\' '
            f'AND time > now() - {hours}h ORDER BY time DESC'
        )
        return self.query(query_str)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "connected": self.client is not None,
            "database": self.config.database,
            "buffered_points": len(self.batch_buffer),
            "total_writes": self.write_count,
            "total_errors": self.error_count,
            "last_write": datetime.fromtimestamp(self.last_write_time).isoformat()
        }
    
    def close(self):
        """Close the InfluxDB connection."""
        try:
            # Flush any remaining points
            if self.batch_buffer:
                logger.info("Flushing remaining points before close...")
                self.flush(force=True)
            
            if self.client:
                self.client.close()
                logger.info("InfluxDB connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Helper functions for common use cases

def create_service(config: Optional[InfluxDBConfig] = None) -> InfluxDBService:
    """
    Factory function to create InfluxDB service instance.
    
    Args:
        config: Optional InfluxDBConfig
        
    Returns:
        InfluxDBService instance
    """
    return InfluxDBService(config)


def parse_kraken_tick_message(message: str) -> TickData:
    """
    Parse Kraken tick message from ZMQ.
    
    Args:
        message: Message string with fields separated by \\x01
        
    Returns:
        TickData object
    """
    fields = message.split('\x01')
    instrument = fields[0]
    ask_price = float(fields[1])
    bid_price = float(fields[5])
    
    base_ccy = None
    term_ccy = None
    
    # Parse currency pairs based on Kraken naming convention
    if instrument[0] == 'X' and instrument[-4] == 'Z':
        base_ccy = instrument[1:4]
        term_ccy = instrument[-3:]
    elif len(instrument) == 6 and instrument[-4] != '_':
        base_ccy = instrument[0:3]
        term_ccy = instrument[3:6]
    
    return TickData(
        instrument=instrument,
        bid=bid_price,
        ask=ask_price,
        base_ccy=base_ccy,
        term_ccy=term_ccy
    )


def parse_oanda_tick_message(message: str) -> TickData:
    """
    Parse OANDA tick message from ZMQ.
    
    Args:
        message: Message string with fields separated by \\x01
        
    Returns:
        TickData object
    """
    fields = message.split('\x01')
    instrument = fields[0]
    timestamp = int(fields[1])
    bid = float(fields[2])
    ask = float(fields[3])
    
    return TickData(
        instrument=instrument,
        bid=bid,
        ask=ask,
        timestamp=timestamp
    )


if __name__ == "__main__":
    # Example usage
    logger.info("Starting InfluxDB Service Example")
    
    # Create service with default config
    with create_service() as service:
        # Write some sample tick data
        tick = TickData(
            instrument="EURUSD",
            bid=1.0856,
            ask=1.0858,
            base_ccy="EUR",
            term_ccy="USD"
        )
        
        service.write_point(tick)
        
        # Manually flush
        service.flush(force=True)
        
        # Get stats
        stats = service.get_stats()
        logger.info(f"Service stats: {json.dumps(stats, indent=2)}")
        
        # Get latest tick
        latest = service.get_latest_tick("EURUSD")
        if latest:
            logger.info(f"Latest EURUSD tick: {latest}")
