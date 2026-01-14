#!/usr/bin/env python3
"""
Setup configuration for nbpy package

nbpy - ZMQ to InfluxDB pipeline for market data
A comprehensive solution for capturing market data via ZMQ and storing it in InfluxDB
with Grafana visualization support.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="nbpy",
    version="1.0.0",
    description="nbpy - ZMQ to InfluxDB pipeline for market data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="textolytics",
    author_email="",
    url="https://github.com/textolytics/nbpy",
    
    # Include all packages automatically
    packages=find_packages(),
    
    # Ensure package data is included
    include_package_data=True,
    
    python_requires=">=3.7",
    
    install_requires=[
        # InfluxDB client
        "influxdb>=5.3.0",
        # ZMQ messaging
        "pyzmq>=22.0.0",
        # MessagePack serialization
        "msgpack>=1.0.0",
    ],
    
    entry_points={
        'console_scripts': [
            # Publishers (12)
            # 'nbpy-pub-betfair-stream = nbpy.zmq.publishers.betfair_stream:main',
            'nbpy-pub-kraken-EURUSD = nbpy.zmq.publishers.kraken_EURUSD:main',
            'nbpy-pub-kraken-EURUSD-depth = nbpy.zmq.publishers.kraken_EURUSD_depth:main',
            'nbpy-pub-kraken-EURUSD-tick = nbpy.zmq.publishers.kraken_EURUSD_tick:main',
            'nbpy-pub-kraken-depth = nbpy.zmq.publishers.kraken_depth:main',
            'nbpy-pub-kraken-orders = nbpy.zmq.publishers.kraken_orders:main',
            'nbpy-pub-kraken-tick = nbpy.zmq.publishers.kraken_tick:main',
            # 'nbpy-pub-oanda = nbpy.zmq.publishers.oanda:main',
            # 'nbpy-pub-oanda-orders = nbpy.zmq.publishers.oanda_orders_:main',
            # 'nbpy-pub-oanda-tick = nbpy.zmq.publishers.oanda_tick:main',
            # 'nbpy-pub-oandav20-tick = nbpy.zmq.publishers.oandav20_tick:main',
            # 'nbpy-pub-oandav20-tick-topic = nbpy.zmq.publishers.oandav20_tick_topic:main',
            
            # Subscribers (27)
            'nbpy-sub-kraken-EURUSD = nbpy.zmq.subscribers.kraken_EURUSD:main',
            'nbpy-sub-kraken-EURUSD-basket = nbpy.zmq.subscribers.kraken_EURUSD_basket:main',
            'nbpy-sub-kraken-EURUSD-depth = nbpy.zmq.subscribers.kraken_EURUSD_depth:main',
            # 'nbpy-sub-kraken-EURUSD-depth-send-order = nbpy.zmq.subscribers.kraken_EURUSD_depth_send_order:main',
            # 'nbpy-sub-kraken-EURUSD-pgsql-tick = nbpy.zmq.subscribers.kraken_EURUSD_pgsql_tick:main',
            # 'nbpy-sub-kraken-EURUSD-tick-grakn = nbpy.zmq.subscribers.kraken_EURUSD_tick_grakn:main',
            'nbpy-sub-kraken-EURUSD-tick-influxdb = nbpy.zmq.subscribers.kraken_EURUSD_tick_influxdb:main',
            # 'nbpy-sub-kraken-EURUSD-tick-pgsql = nbpy.zmq.subscribers.kraken_EURUSD_tick_pgsql:main',
            'nbpy-sub-kraken-basic-stat-influxdb-tick = nbpy.zmq.subscribers.kraken_basic_stat_influxdb_tick:main',
            # 'nbpy-sub-kraken-basic-stat-tick-cuda = nbpy.zmq.subscribers.kraken_basic_stat_tick_cuda:main',
            # 'nbpy-sub-kraken-basic-stat-tick-pd = nbpy.zmq.subscribers.kraken_basic_stat_tick_pd:main',
            'nbpy-sub-kraken-influxdb = nbpy.zmq.subscribers.kraken_influxdb:main',
            'nbpy-sub-kraken-influxdb-EURUSD-basket = nbpy.zmq.subscribers.kraken_influxdb_EURUSD_basket:main',
            'nbpy-sub-kraken-influxdb-depth = nbpy.zmq.subscribers.kraken_influxdb_depth:main',
            'nbpy-sub-kraken-influxdb-depth-base-term = nbpy.zmq.subscribers.kraken_influxdb_depth_base_term:main',
            # 'nbpy-sub-kraken-influxdb-orders = nbpy.zmq.subscribers.kraken_influxdb_orders:main',
            # 'nbpy-sub-kraken-influxdb-tick = nbpy.zmq.subscribers.kraken_influxdb_tick:main',
            'nbpy-sub-kraken-kapacitor-EURUSD = nbpy.zmq.subscribers.kraken_kapacitor_EURUSD:main',
            # 'nbpy-sub-kraken-kapacitor-orders = nbpy.zmq.subscribers.kraken_kapacitor_orders:main',
            # 'nbpy-sub-oanda-influxdb = nbpy.zmq.subscribers.oanda_influxdb:main',
            # 'nbpy-sub-oanda-influxdb-tick = nbpy.zmq.subscribers.oanda_influxdb_tick:main',
            # 'nbpy-sub-oanda-kraken-EURUSD-depth-position-order = nbpy.zmq.subscribers.oanda_kraken_EURUSD_depth_position_order:main',
            # 'nbpy-sub-oanda-kraken-EURUSD-depth-position-order-update = nbpy.zmq.subscribers.oanda_kraken_EURUSD_depth_position_order_update:main',
            # 'nbpy-sub-oanda-kraken-EURUSD-tick-position-order = nbpy.zmq.subscribers.oanda_kraken_EURUSD_tick_position_order:main',
            # # 'nbpy-sub-oanda-pgsql-tick = nbpy.zmq.subscribers.oanda_pgsql_tick:main',
            # 'nbpy-sub-twitter-influx-sentiment-location = nbpy.zmq.subscribers.twitter_influx_sentiment_location:main',
            # 'nbpy-sub-twitter-pgsql-sentiment-location = nbpy.zmq.subscribers.twitter_pgsql_sentiment_location:main',
            
            # Example services
            'nbpy-sub-influxdb-tick = nbpy.zmq.subscribers.influxdb_tick:main',
        ],
    },
    
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
        "docker": [
            "docker>=5.0",
            "docker-compose>=1.29",
        ],
        "all": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "docker>=5.0",
            "docker-compose>=1.29",
        ],
    },
    
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    
    keywords="influxdb zmq timeseries database market data financial",
    
    project_urls={
        "Bug Reports": "https://github.com/textolytics/nbpy/issues",
        "Source": "https://github.com/textolytics/nbpy",
        "Documentation": "https://github.com/textolytics/nbpy/docs",
    },
)
