#!/usr/bin/env python3
"""
Example usage of the nbpy.db module for InfluxDB storage.

This script demonstrates:
1. Basic InfluxDB service creation and data writing
2. Different data types (Tick, Depth, OHLC, Sentiment)
3. Configuration management
4. ZMQ bridge integration
5. Querying stored data
"""

import sys
import logging
from pathlib import Path

# Add nbpy to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import (
    InfluxDBService,
    InfluxDBConfig,
    TickData,
    DepthData,
    OHLCData,
    SentimentData,
    create_service,
    get_config_manager,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_service():
    """Example 1: Basic InfluxDB service"""
    logger.info("=" * 60)
    logger.info("Example 1: Basic InfluxDB Service")
    logger.info("=" * 60)
    
    with create_service() as service:
        # Create tick data
        tick = TickData(
            instrument="EURUSD",
            bid=1.0856,
            ask=1.0858,
            base_ccy="EUR",
            term_ccy="USD"
        )
        
        # Write to InfluxDB
        service.write_point(tick)
        logger.info(f"Written tick: {tick}")
        
        # Flush to database
        service.flush(force=True)
        
        # Get statistics
        stats = service.get_stats()
        logger.info(f"Service stats: {stats}")


def example_batch_writing():
    """Example 2: Batch writing multiple data points"""
    logger.info("=" * 60)
    logger.info("Example 2: Batch Writing")
    logger.info("=" * 60)
    
    with create_service() as service:
        # Create multiple tick data points
        ticks = [
            TickData(instrument="EURUSD", bid=1.0856, ask=1.0858, base_ccy="EUR", term_ccy="USD"),
            TickData(instrument="GBPUSD", bid=1.2650, ask=1.2652, base_ccy="GBP", term_ccy="USD"),
            TickData(instrument="USDJPY", bid=110.45, ask=110.47, base_ccy="USD", term_ccy="JPY"),
        ]
        
        # Write all points
        service.write_points(ticks)
        logger.info(f"Written {len(ticks)} tick data points")
        
        # Flush
        service.flush(force=True)
        logger.info("Flushed to InfluxDB")


def example_different_data_types():
    """Example 3: Different data types"""
    logger.info("=" * 60)
    logger.info("Example 3: Different Data Types")
    logger.info("=" * 60)
    
    with create_service() as service:
        # Tick data
        tick = TickData(
            instrument="EURUSD",
            bid=1.0856,
            ask=1.0858,
            volume=1000000
        )
        service.write_point(tick)
        logger.info("Written TickData")
        
        # Depth data
        depth = DepthData(
            instrument="EURUSD",
            bid_prices=[1.0856, 1.0855, 1.0854],
            bid_volumes=[1000000, 500000, 250000],
            ask_prices=[1.0858, 1.0859, 1.0860],
            ask_volumes=[1000000, 500000, 250000]
        )
        service.write_point(depth)
        logger.info("Written DepthData")
        
        # OHLC data
        ohlc = OHLCData(
            instrument="EURUSD",
            open=1.0850,
            high=1.0860,
            low=1.0845,
            close=1.0858,
            volume=1000000,
            trades=5000
        )
        service.write_point(ohlc)
        logger.info("Written OHLCData")
        
        # Sentiment data
        sentiment = SentimentData(
            source="twitter",
            instrument="EURUSD",
            sentiment_score=0.75,
            text="EUR is strengthening",
            location="global"
        )
        service.write_point(sentiment)
        logger.info("Written SentimentData")
        
        # Flush all
        service.flush(force=True)
        logger.info("Flushed all data types to InfluxDB")


def example_configuration():
    """Example 4: Configuration management"""
    logger.info("=" * 60)
    logger.info("Example 4: Configuration Management")
    logger.info("=" * 60)
    
    # Get global config manager
    config_mgr = get_config_manager()
    
    # Get base configuration
    base_config = config_mgr.get_base_config()
    logger.info(f"Base config keys: {list(base_config.keys())}")
    
    # Get service-specific config
    tick_config = config_mgr.get_service_config('tick')
    logger.info(f"Tick service config: {tick_config}")
    
    # Create service with custom config
    custom_config = InfluxDBConfig(
        host="localhost",
        port=8086,
        database="custom_db",
        batch_size=100
    )
    
    service = InfluxDBService(custom_config)
    logger.info(f"Created service with custom config")
    logger.info(f"Stats: {service.get_stats()}")
    service.close()


def example_custom_config():
    """Example 5: Custom InfluxDB configuration"""
    logger.info("=" * 60)
    logger.info("Example 5: Custom Configuration")
    logger.info("=" * 60)
    
    config = InfluxDBConfig(
        host="localhost",
        port=8086,
        username="zmq",
        password="zmq",
        database="market_data",
        batch_size=1000,
        timeout=15
    )
    
    service = InfluxDBService(config)
    logger.info(f"Connected with custom config")
    logger.info(f"Database: {config.database}")
    logger.info(f"Batch size: {config.batch_size}")
    
    # Test write
    tick = TickData(instrument="TEST", bid=1.0, ask=1.001)
    service.write_point(tick)
    service.flush(force=True)
    
    service.close()


def example_context_manager():
    """Example 6: Using context manager"""
    logger.info("=" * 60)
    logger.info("Example 6: Context Manager Usage")
    logger.info("=" * 60)
    
    # Context manager automatically closes connection
    with create_service() as service:
        # Write data
        tick = TickData(instrument="EURUSD", bid=1.0856, ask=1.0858)
        service.write_point(tick)
        
        # Get stats before closing
        stats = service.get_stats()
        logger.info(f"Buffered points: {stats['buffered_points']}")
        
        # Flush
        service.flush(force=True)
        logger.info("Service closed automatically on exit")


def example_querying():
    """Example 7: Querying data"""
    logger.info("=" * 60)
    logger.info("Example 7: Querying Data")
    logger.info("=" * 60)
    
    with create_service() as service:
        # Query latest tick
        latest = service.get_latest_tick("EURUSD")
        if latest:
            logger.info(f"Latest EURUSD tick: {latest}")
        else:
            logger.info("No EURUSD tick data found")
        
        # Query OHLC data
        ohlc_data = service.get_ohlc("EURUSD", hours=24)
        if ohlc_data:
            logger.info(f"Found {len(ohlc_data)} OHLC candles for EURUSD")
        else:
            logger.info("No OHLC data found")
        
        # Custom query
        try:
            results = service.query('SELECT * FROM "tick" LIMIT 5')
            logger.info(f"Custom query returned: {len(results) if results else 0} points")
        except Exception as e:
            logger.warning(f"Query failed: {e}")


def example_error_handling():
    """Example 8: Error handling"""
    logger.info("=" * 60)
    logger.info("Example 8: Error Handling")
    logger.info("=" * 60)
    
    try:
        service = InfluxDBService()
        
        if not service.client:
            logger.warning("Not connected to InfluxDB")
            if service.reconnect():
                logger.info("Successfully reconnected")
            else:
                logger.error("Failed to reconnect")
        
        # Check statistics
        stats = service.get_stats()
        logger.info(f"Error count: {stats['total_errors']}")
        
        service.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def main():
    """Run all examples"""
    logger.info("Starting nbpy.db usage examples")
    
    try:
        # Run each example
        examples = [
            ("Basic Service", example_basic_service),
            ("Batch Writing", example_batch_writing),
            ("Different Data Types", example_different_data_types),
            ("Configuration", example_configuration),
            ("Custom Config", example_custom_config),
            ("Context Manager", example_context_manager),
            ("Error Handling", example_error_handling),
        ]
        
        for name, example_func in examples:
            try:
                example_func()
                logger.info(f"✓ {name} completed\n")
            except Exception as e:
                logger.error(f"✗ {name} failed: {e}\n")
        
        logger.info("=" * 60)
        logger.info("All examples completed")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
