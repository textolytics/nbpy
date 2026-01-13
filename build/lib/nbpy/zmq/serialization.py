"""
ZMQ Message Serialization and Deserialization

This module provides utilities for serializing/deserializing messages
using MessagePack format for all ZMQ communication.
"""

import msgpack
import json
import logging
from typing import Any, Union, Dict, List

logger = logging.getLogger(__name__)


class MessagePackCodec:
    """Codec for MessagePack serialization/deserialization"""
    
    @staticmethod
    def pack(data: Any) -> bytes:
        """Pack data into MessagePack binary format"""
        try:
            return msgpack.packb(data, use_bin_type=True, default=str)
        except Exception as e:
            logger.error(f"Failed to pack data: {e}")
            raise
    
    @staticmethod
    def unpack(data: bytes) -> Any:
        """Unpack MessagePack binary format into Python objects"""
        try:
            return msgpack.unpackb(data, raw=False)
        except Exception as e:
            logger.error(f"Failed to unpack data: {e}")
            raise
    
    @staticmethod
    def pack_json(data: Union[dict, list, str]) -> bytes:
        """Convert JSON-compatible data to MessagePack"""
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return MessagePackCodec.pack(data)
        except Exception as e:
            logger.error(f"Failed to pack JSON as MessagePack: {e}")
            raise


class ZMQMessageHandler:
    """Handler for ZMQ message serialization across PUB/SUB sockets"""
    
    @staticmethod
    def serialize_message(topic: str, data: Any) -> bytes:
        """
        Serialize a topic and data into multipart ZMQ message format
        
        Format: [topic_as_binary, data_as_msgpack]
        """
        try:
            topic_bytes = topic.encode('utf-8') if isinstance(topic, str) else topic
            data_bytes = MessagePackCodec.pack(data)
            return topic_bytes + b' ' + data_bytes
        except Exception as e:
            logger.error(f"Failed to serialize message: {e}")
            raise
    
    @staticmethod
    def serialize_multipart(topic: str, data: Any) -> List[bytes]:
        """
        Serialize as ZMQ multipart message
        
        Returns: [topic_bytes, data_bytes]
        """
        try:
            topic_bytes = topic.encode('utf-8') if isinstance(topic, str) else topic
            data_bytes = MessagePackCodec.pack(data)
            return [topic_bytes, data_bytes]
        except Exception as e:
            logger.error(f"Failed to serialize multipart message: {e}")
            raise
    
    @staticmethod
    def deserialize_message(message: Union[bytes, str]) -> tuple:
        """
        Deserialize ZMQ message into (topic, data) tuple
        
        Handles both single-part and multipart messages
        """
        try:
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            # Split on first space
            parts = message.split(b' ', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid message format, expected 2 parts: {message}")
            
            topic = parts[0].decode('utf-8')
            data = MessagePackCodec.unpack(parts[1])
            return topic, data
        except Exception as e:
            logger.error(f"Failed to deserialize message: {e}")
            raise
    
    @staticmethod
    def deserialize_multipart(message_parts: List[bytes]) -> tuple:
        """
        Deserialize ZMQ multipart message
        
        Expects: [topic_bytes, data_bytes]
        """
        try:
            if len(message_parts) != 2:
                raise ValueError(f"Expected 2 message parts, got {len(message_parts)}")
            
            topic = message_parts[0].decode('utf-8')
            data = MessagePackCodec.unpack(message_parts[1])
            return topic, data
        except Exception as e:
            logger.error(f"Failed to deserialize multipart message: {e}")
            raise


def convert_json_to_msgpack(json_data: Union[str, dict]) -> bytes:
    """Convenience function to convert JSON to MessagePack"""
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    return MessagePackCodec.pack(json_data)


def convert_msgpack_to_json(msgpack_data: bytes) -> dict:
    """Convenience function to convert MessagePack to JSON-compatible dict"""
    return MessagePackCodec.unpack(msgpack_data)
