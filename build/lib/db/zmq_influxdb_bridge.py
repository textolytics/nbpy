"""
ZMQ Service Integration for InfluxDB

This module provides ZMQ subscriber implementations that automatically
forward data from ZMQ publishers to InfluxDB for persistence.
"""

import zmq
import logging
import signal
import sys
from typing import Optional, Callable, Dict, Any
from threading import Thread, Event
import time

from .influxdb_service import (
    InfluxDBService,
    InfluxDBConfig,
    TickData,
    DepthData,
    parse_kraken_tick_message,
    parse_oanda_tick_message,
)


logger = logging.getLogger(__name__)


class ZMQInfluxDBBridge:
    """
    Bridge between ZMQ publishers and InfluxDB storage.
    
    Subscribes to ZMQ topics and persists data to InfluxDB in real-time.
    """
    
    def __init__(
        self,
        zmq_host: str = "localhost",
        zmq_port: int = 5556,
        topic_filter: str = "",
        influxdb_config: Optional[InfluxDBConfig] = None,
        service_name: str = "zmq_influxdb_bridge"
    ):
        """
        Initialize ZMQ-InfluxDB bridge.
        
        Args:
            zmq_host: ZMQ server host
            zmq_port: ZMQ server port
            topic_filter: Topic filter for subscription
            influxdb_config: InfluxDB configuration
            service_name: Service name for logging
        """
        self.zmq_host = zmq_host
        self.zmq_port = zmq_port
        self.topic_filter = topic_filter
        self.service_name = service_name
        
        # Initialize InfluxDB service
        self.influxdb_service = InfluxDBService(influxdb_config)
        
        # ZMQ setup
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        
        # Control flags
        self.running = False
        self.stop_event = Event()
        
        # Statistics
        self.messages_received = 0
        self.messages_written = 0
        self.errors = 0
        
        # Message parser (can be overridden)
        self.message_parser: Optional[Callable[[str], Any]] = None
        
        logger.info(f"Initialized ZMQInfluxDBBridge: {service_name}")
    
    def connect_zmq(self) -> bool:
        """
        Connect to ZMQ publisher.
        
        Returns:
            True if connection successful
        """
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            
            if self.topic_filter:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic_filter)
            else:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
            
            connection_string = f"tcp://{self.zmq_host}:{self.zmq_port}"
            self.socket.connect(connection_string)
            
            logger.info(f"Connected to ZMQ: {connection_string} (filter: {self.topic_filter})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ZMQ: {e}")
            return False
    
    def disconnect_zmq(self):
        """Disconnect from ZMQ"""
        try:
            if self.socket:
                self.socket.close()
            if self.context:
                self.context.term()
            logger.info("Disconnected from ZMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from ZMQ: {e}")
    
    def set_message_parser(self, parser: Callable[[str], Any]):
        """
        Set custom message parser function.
        
        Args:
            parser: Function that takes message string and returns data object
        """
        self.message_parser = parser
    
    def _process_message(self, message: str) -> bool:
        """
        Process a single message.
        
        Args:
            message: Raw message string
            
        Returns:
            True if processed successfully
        """
        try:
            if self.message_parser:
                data_point = self.message_parser(message)
            else:
                # Default: treat as raw dict
                logger.warning("No message parser configured, skipping message")
                return False
            
            if data_point:
                self.influxdb_service.write_point(data_point)
                self.messages_written += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.errors += 1
            return False
    
    def run(self, blocking: bool = True):
        """
        Start the bridge (receive and forward messages).
        
        Args:
            blocking: If True, run in current thread; if False, run in background
        """
        if blocking:
            self._run()
        else:
            thread = Thread(target=self._run, daemon=True)
            thread.start()
    
    def _run(self):
        """Internal run loop"""
        if not self.connect_zmq():
            logger.error("Failed to initialize ZMQ connection")
            return
        
        self.running = True
        
        try:
            while self.running and not self.stop_event.is_set():
                try:
                    # Non-blocking receive with timeout
                    message = self.socket.recv_string(zmq.NOBLOCK)
                    self.messages_received += 1
                    
                    # Process message
                    self._process_message(message)
                    
                    # Periodic flush
                    if self.messages_written % 100 == 0:
                        self.influxdb_service.flush()
                    
                except zmq.Again:
                    # No message available, sleep briefly
                    time.sleep(0.01)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.errors += 1
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bridge"""
        logger.info("Stopping ZMQInfluxDBBridge...")
        self.running = False
        self.stop_event.set()
        
        # Flush remaining data
        self.influxdb_service.flush(force=True)
        
        # Cleanup
        self.disconnect_zmq()
        self.influxdb_service.close()
        
        # Log statistics
        self.log_stats()
    
    def log_stats(self):
        """Log bridge statistics"""
        logger.info(f"Bridge Statistics for {self.service_name}:")
        logger.info(f"  Messages received: {self.messages_received}")
        logger.info(f"  Messages written: {self.messages_written}")
        logger.info(f"  Errors: {self.errors}")
        
        influxdb_stats = self.influxdb_service.get_stats()
        logger.info(f"  InfluxDB writes: {influxdb_stats['total_writes']}")
        logger.info(f"  InfluxDB errors: {influxdb_stats['total_errors']}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics.
        
        Returns:
            Dictionary with statistics
        """
        influxdb_stats = self.influxdb_service.get_stats()
        
        return {
            "service_name": self.service_name,
            "running": self.running,
            "zmq_host": self.zmq_host,
            "zmq_port": self.zmq_port,
            "topic_filter": self.topic_filter,
            "messages_received": self.messages_received,
            "messages_written": self.messages_written,
            "errors": self.errors,
            "influxdb": influxdb_stats
        }


class KrakenTickBridge(ZMQInfluxDBBridge):
    """Bridge for Kraken tick data"""
    
    def __init__(self, zmq_port: int = 5558, influxdb_config: Optional[InfluxDBConfig] = None):
        """
        Initialize Kraken tick bridge.
        
        Args:
            zmq_port: ZMQ publisher port
            influxdb_config: InfluxDB configuration
        """
        super().__init__(
            zmq_port=zmq_port,
            topic_filter="kraken_tick",
            influxdb_config=influxdb_config,
            service_name="kraken_tick_bridge"
        )
        self.set_message_parser(self._parse_kraken_message)
    
    def _parse_kraken_message(self, message: str) -> Optional[TickData]:
        """Parse Kraken tick message"""
        try:
            topic, messagedata = message.split(' ', 1)
            return parse_kraken_tick_message(messagedata)
        except Exception as e:
            logger.error(f"Error parsing Kraken message: {e}")
            return None


class OandaTickBridge(ZMQInfluxDBBridge):
    """Bridge for OANDA tick data"""
    
    def __init__(self, zmq_port: int = 5556, influxdb_config: Optional[InfluxDBConfig] = None):
        """
        Initialize OANDA tick bridge.
        
        Args:
            zmq_port: ZMQ publisher port
            influxdb_config: InfluxDB configuration
        """
        super().__init__(
            zmq_port=zmq_port,
            topic_filter="oanda_tick",
            influxdb_config=influxdb_config,
            service_name="oanda_tick_bridge"
        )
        self.set_message_parser(self._parse_oanda_message)
    
    def _parse_oanda_message(self, message: str) -> Optional[TickData]:
        """Parse OANDA tick message"""
        try:
            topic, messagedata = message.split(' ', 1)
            return parse_oanda_tick_message(messagedata)
        except Exception as e:
            logger.error(f"Error parsing OANDA message: {e}")
            return None


class GenericZMQBridge(ZMQInfluxDBBridge):
    """Generic bridge for custom ZMQ sources"""
    
    def __init__(
        self,
        zmq_port: int,
        topic_filter: str,
        parser_func: Callable[[str], Any],
        service_name: str = "generic_zmq_bridge",
        influxdb_config: Optional[InfluxDBConfig] = None
    ):
        """
        Initialize generic ZMQ bridge.
        
        Args:
            zmq_port: ZMQ publisher port
            topic_filter: Topic filter for subscription
            parser_func: Function to parse messages
            service_name: Service name
            influxdb_config: InfluxDB configuration
        """
        super().__init__(
            zmq_port=zmq_port,
            topic_filter=topic_filter,
            influxdb_config=influxdb_config,
            service_name=service_name
        )
        self.set_message_parser(lambda msg: self._parse_with_topic(msg, parser_func))
    
    def _parse_with_topic(self, message: str, parser_func: Callable[[str], Any]) -> Optional[Any]:
        """Parse message with custom function"""
        try:
            topic, messagedata = message.split(' ', 1)
            return parser_func(messagedata)
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None


# Convenience functions

def create_kraken_bridge(zmq_port: int = 5558) -> KrakenTickBridge:
    """Create and return a Kraken tick bridge"""
    return KrakenTickBridge(zmq_port=zmq_port)


def create_oanda_bridge(zmq_port: int = 5556) -> OandaTickBridge:
    """Create and return an OANDA tick bridge"""
    return OandaTickBridge(zmq_port=zmq_port)


def create_generic_bridge(
    zmq_port: int,
    topic_filter: str,
    parser_func: Callable[[str], Any],
    service_name: str = "generic_bridge"
) -> GenericZMQBridge:
    """Create and return a generic ZMQ bridge"""
    return GenericZMQBridge(zmq_port, topic_filter, parser_func, service_name)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run Kraken bridge
    print("Starting Kraken Tick Bridge...")
    bridge = create_kraken_bridge(zmq_port=5558)
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutdown signal received")
        bridge.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run bridge
    bridge.run(blocking=True)
