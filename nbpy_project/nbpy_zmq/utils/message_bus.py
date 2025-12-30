"""Message bus abstraction layer for ZMQ pub/sub."""

import zmq
import logging
from typing import Optional, List
from .config import ZMQConfig


logger = logging.getLogger(__name__)


class MessageBus:
    """ZMQ-based message bus for pub/sub communication."""
    
    def __init__(self, config: Optional[ZMQConfig] = None):
        """Initialize message bus.
        
        Args:
            config: ZMQConfig instance. Uses defaults if None.
        """
        self.config = config or ZMQConfig()
        self.context = zmq.Context()
        self._pub_socket = None
        self._sub_socket = None
    
    def create_publisher(self, port: Optional[int] = None, host: Optional[str] = None) -> zmq.Socket:
        """Create a ZMQ publisher socket.
        
        Args:
            port: Port to bind to. Uses config.pub_port if None.
            host: Host to bind to. Uses config.host if None.
            
        Returns:
            ZMQ PUB socket.
        """
        _port = port or self.config.pub_port
        _host = host or self.config.host
        
        socket = self.context.socket(zmq.PUB)
        url = f"tcp://{_host}:{_port}"
        socket.bind(url)
        logger.info(f"Publisher bound to {url}")
        
        self._pub_socket = socket
        return socket
    
    def create_subscriber(
        self, 
        topics: List[str],
        port: Optional[int] = None,
        host: Optional[str] = None
    ) -> zmq.Socket:
        """Create a ZMQ subscriber socket.
        
        Args:
            topics: List of topics to subscribe to.
            port: Port to connect to. Uses config.pub_port if None.
            host: Host to connect to. Uses config.host if None.
            
        Returns:
            ZMQ SUB socket.
        """
        _port = port or self.config.pub_port
        _host = host or self.config.host
        
        socket = self.context.socket(zmq.SUB)
        
        for topic in topics:
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        
        url = f"tcp://{_host}:{_port}"
        socket.connect(url)
        logger.info(f"Subscriber connected to {url}, topics: {topics}")
        
        self._sub_socket = socket
        return socket
    
    def send_message(self, topic: str, data: str) -> None:
        """Publish a message.
        
        Args:
            topic: Message topic.
            data: Message payload.
        """
        if not self._pub_socket:
            raise RuntimeError("Publisher not initialized. Call create_publisher() first.")
        
        message = f"{topic} {data}"
        self._pub_socket.send_string(message)
        logger.debug(f"Published to {topic}: {data[:50]}...")
    
    def receive_message(self) -> tuple[str, str]:
        """Receive a message.
        
        Returns:
            Tuple of (topic, data).
        """
        if not self._sub_socket:
            raise RuntimeError("Subscriber not initialized. Call create_subscriber() first.")
        
        message = self._sub_socket.recv_string()
        parts = message.split(' ', 1)
        
        if len(parts) == 2:
            return parts[0], parts[1]
        return parts[0], ""
    
    def close(self) -> None:
        """Close all sockets and context."""
        if self._pub_socket:
            self._pub_socket.close()
        if self._sub_socket:
            self._sub_socket.close()
        self.context.term()
        logger.info("Message bus closed")
