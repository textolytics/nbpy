"""
nbpy - ZMQ to InfluxDB Pipeline for Market Data

A comprehensive solution for capturing market data via ZMQ and storing it 
in InfluxDB with Grafana visualization support.

Main submodules:
    db: Database and InfluxDB integration
    zmq: ZMQ pub/sub microservices framework
"""

__version__ = "1.0.0"
__author__ = "textolytics"

# Import main modules for easy access
try:
    from . import db
    from . import zmq
except ImportError:
    pass

__all__ = [
    'db',
    'zmq',
    '__version__',
    '__author__',
]
