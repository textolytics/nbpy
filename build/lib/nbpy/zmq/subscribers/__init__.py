"""
nbpy.zmq.subscribers - Subscriber Microservices

This submodule contains all migrated subscriber implementations for various backends.
Subscribers inherit from backend-specific base classes and handle data persistence.

Backends:
- InfluxDB: Time-series storage for market data (15+ subscribers)
- PostgreSQL: Relational storage (3+ subscribers)
- Grakn: Graph database (1 subscriber)
- Kapacitor: Stream processing (2 subscribers)
- CUDA/Pandas: Statistical processing (2 subscribers)
- Composite: Multi-source aggregation (3+ subscribers)
"""

__all__ = [
    # Example services
    'influxdb_tick',
    
    # Kraken InfluxDB subscribers
    'kraken_influxdb',
    'kraken_influxdb_tick',
    'kraken_influxdb_depth',
    'kraken_influxdb_orders',
    'kraken_influxdb_EURUSD_basket',
    'kraken_influxdb_depth_base_term',
    'kraken_basic_stat_influxdb_tick',
    
    # # Kraken PostgreSQL subscribers
    # 'kraken_EURUSD_pgsql_tick',
    # 'kraken_EURUSD_tick_pgsql',
    
    # Kraken other subscribers
    'kraken_EURUSD',
    'kraken_EURUSD_basket',
    'kraken_EURUSD_depth',
    'kraken_EURUSD_depth_send_order',
    'kraken_EURUSD_tick_grakn',
    'kraken_basic_stat_tick_cuda',
    'kraken_basic_stat_tick_pd',
    'kraken_kapacitor_EURUSD',
    'kraken_kapacitor_orders',
    
    # OANDA subscribers
    # 'oanda_influxdb',
    # 'oanda_influxdb_tick',
    # 'oanda_pgsql_tick',
    # 'oanda_kraken_EURUSD_depth_position_order',
    # 'oanda_kraken_EURUSD_depth_position_order_update',
    # 'oanda_kraken_EURUSD_tick_position_order',
    
    # Twitter subscribers
    # 'twitter_influx_sentiment_location',
    # 'twitter_pgsql_sentiment_location',
]

