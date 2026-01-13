"""
Base ZMQ Publisher and Subscriber Classes

Provides base classes for all PUB and SUB microservices with
proper error handling, logging, and MessagePack serialization.
"""

import zmq
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any, Callable
import signal
import sys

from .serialization import ZMQMessageHandler, MessagePackCodec
from .ports import PortConfig

logger = logging.getLogger(__name__)


class BaseZMQService(ABC):
    """Base class for all ZMQ services"""
    
    def __init__(self, port_config: PortConfig, context: Optional[zmq.Context] = None):
        self.port_config = port_config
        self.context = context or zmq.Context()
        self.socket = None
        self.running = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Initialized {self.__class__.__name__} for {port_config.service_name}")
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals gracefully"""
        logger.info(f"Received signal {sig}, shutting down...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources"""
        if self.socket:
            try:
                self.socket.close()
                logger.info(f"Closed socket for {self.port_config.service_name}")
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        try:
            self.context.term()
            logger.info("Terminated ZMQ context")
        except Exception as e:
            logger.error(f"Error terminating context: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class BasePublisher(BaseZMQService):
    """Base class for ZMQ PUB services"""
    
    def __init__(self, port_config: PortConfig, context: Optional[zmq.Context] = None):
        super().__init__(port_config, context)
        self.socket = self.context.socket(zmq.PUB)
        self._setup_socket()
    
    def _setup_socket(self):
        """Configure publisher socket"""
        try:
            # Bind to all interfaces
            endpoint = f"tcp://*:{self.port_config.port}"
            self.socket.bind(endpoint)
            logger.info(f"Publisher bound to {endpoint}")
            
            # Optional: Set high water mark to prevent message loss
            # self.socket.setsockopt(zmq.SNDHWM, 10000)
            
        except zmq.error.ZMQError as e:
            logger.error(f"Failed to bind socket: {e}")
            raise
    
    def publish_msgpack(self, topic: str, data: Any) -> None:
        """
        Publish data as MessagePack
        
        Args:
            topic: Topic string
            data: Data to serialize and publish
        """
        try:
            message = ZMQMessageHandler.serialize_multipart(topic, data)
            self.socket.send_multipart(message)
            logger.debug(f"Published to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
    
    def publish_json(self, topic: str, data: Any) -> None:
        """
        Publish JSON-serializable data as MessagePack
        
        Args:
            topic: Topic string
            data: JSON-serializable data
        """
        try:
            message = ZMQMessageHandler.serialize_multipart(topic, data)
            self.socket.send_multipart(message)
            logger.debug(f"Published to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish JSON message: {e}")
            raise
    
    def publish_raw(self, topic: str, data: bytes) -> None:
        """
        Publish raw binary data
        
        Args:
            topic: Topic string
            data: Raw bytes to publish
        """
        try:
            topic_bytes = topic.encode('utf-8') if isinstance(topic, str) else topic
            self.socket.send_multipart([topic_bytes, data])
            logger.debug(f"Published raw message to {topic}")
        except Exception as e:
            logger.error(f"Failed to publish raw message: {e}")
            raise


class BaseSubscriber(BaseZMQService):
    """Base class for ZMQ SUB services"""
    
    def __init__(
        self, 
        port_config: PortConfig, 
        host: str = "localhost",
        context: Optional[zmq.Context] = None
    ):
        super().__init__(port_config, context)
        self.host = host
        self.socket = self.context.socket(zmq.SUB)
        self._setup_socket()
        self.message_handler: Optional[Callable[[str, Any], None]] = None
    
    def _setup_socket(self):
        """Configure subscriber socket"""
        try:
            # Subscribe to topic filter if specified
            if self.port_config.topic_filter:
                topic = self.port_config.topic_filter.encode('utf-8')
                self.socket.setsockopt(zmq.SUBSCRIBE, topic)
                logger.info(f"Subscribed to topic: {self.port_config.topic_filter}")
            else:
                # Subscribe to all messages
                self.socket.setsockopt(zmq.SUBSCRIBE, b'')
                logger.info("Subscribed to all messages")
            
            # Connect to publisher
            endpoint = f"tcp://{self.host}:{self.port_config.port}"
            self.socket.connect(endpoint)
            logger.info(f"Subscriber connected to {endpoint}")
            
            # Optional: Set high water mark
            # self.socket.setsockopt(zmq.RCVHWM, 10000)
            
        except zmq.error.ZMQError as e:
            logger.error(f"Failed to setup subscriber socket: {e}")
            raise
    
    def set_message_handler(self, handler: Callable[[str, Any], None]) -> None:
        """Set callback handler for received messages"""
        self.message_handler = handler
    
    def recv_msgpack(self) -> tuple:
        """
        Receive and deserialize MessagePack message
        
        Returns:
            (topic, data) tuple
        """
        try:
            message_parts = self.socket.recv_multipart()
            return ZMQMessageHandler.deserialize_multipart(message_parts)
        except Exception as e:
            logger.error(f"Failed to receive MessagePack message: {e}")
            raise
    
    def recv_raw(self) -> tuple:
        """
        Receive raw message
        
        Returns:
            (topic_bytes, data_bytes) tuple
        """
        try:
            return self.socket.recv_multipart()
        except Exception as e:
            logger.error(f"Failed to receive raw message: {e}")
            raise
    
    def run(self, timeout: Optional[int] = None) -> None:
        """
        Run the subscriber loop
        
        Args:
            timeout: Timeout in milliseconds (None for blocking)
        """
        self.running = True
        logger.info(f"Starting subscriber loop for {self.port_config.service_name}")
        
        try:
            while self.running:
                if timeout is not None:
                    if self.socket.poll(timeout) == 0:
                        continue
                
                topic, data = self.recv_msgpack()
                
                if self.message_handler:
                    try:
                        self.message_handler(topic, data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
                else:
                    logger.warning(f"No message handler set. Received: {topic}")
        
        except KeyboardInterrupt:
            logger.info("Subscriber interrupted by user")
        except Exception as e:
            logger.error(f"Subscriber error: {e}")
        finally:
            self.cleanup()
    
    def stop(self) -> None:
        """Stop the subscriber loop"""
        self.running = False
        logger.info("Stopping subscriber")
