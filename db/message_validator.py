#!/usr/bin/env python3
"""
ZMQ Message Streaming Validator

Validates that:
1. Publishers are streaming messages on their topics
2. Subscribers are receiving and forwarding messages
3. InfluxDB is persisting the data
4. Data flow is continuous and healthy
"""

import zmq
import json
import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from threading import Thread, Event
from collections import defaultdict
from datetime import datetime
from influxdb import InfluxDBClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/message_validator.log')
    ]
)
logger = logging.getLogger(__name__)


class TopicMonitor:
    """Monitors messages on a single ZMQ topic"""
    
    def __init__(self, topic: str, zmq_host: str = 'localhost', zmq_port: int = 5556):
        self.topic = topic
        self.zmq_host = zmq_host
        self.zmq_port = zmq_port
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.running = False
        self.stop_event = Event()
        
        self.message_count = 0
        self.first_message_time: Optional[datetime] = None
        self.last_message_time: Optional[datetime] = None
        self.error_count = 0
        self.messages: List[Any] = []
    
    def connect(self, timeout: int = 5) -> bool:
        """Connect to ZMQ publisher"""
        try:
            logger.info(f"Connecting to {self.zmq_host}:{self.zmq_port} for topic '{self.topic}'...")
            
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
            self.socket.setsockopt(zmq.RCVTIMEO, timeout * 1000)
            
            endpoint = f"tcp://{self.zmq_host}:{self.zmq_port}"
            self.socket.connect(endpoint)
            
            logger.info(f"✓ Connected to ZMQ on {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ZMQ: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from ZMQ"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        if self.context:
            try:
                self.context.term()
            except Exception as e:
                logger.error(f"Error terminating context: {e}")
    
    def receive_messages(self, duration: int = 10) -> bool:
        """Receive messages for specified duration"""
        self.running = True
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                try:
                    message = self.socket.recv_multipart()
                    
                    if self.first_message_time is None:
                        self.first_message_time = datetime.now()
                    
                    self.last_message_time = datetime.now()
                    self.message_count += 1
                    self.messages.append(message)
                    
                    logger.debug(f"Received message on {self.topic} (count: {self.message_count})")
                
                except zmq.error.Again:
                    # Timeout waiting for message, continue loop
                    continue
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    self.error_count += 1
            
            self.running = False
            return self.message_count > 0
        
        except KeyboardInterrupt:
            self.running = False
            return False
        finally:
            self.disconnect()
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        uptime = None
        message_rate = 0
        
        if self.first_message_time and self.last_message_time:
            uptime = (self.last_message_time - self.first_message_time).total_seconds()
            if uptime > 0:
                message_rate = self.message_count / uptime
        
        return {
            'topic': self.topic,
            'message_count': self.message_count,
            'error_count': self.error_count,
            'first_message': self.first_message_time.isoformat() if self.first_message_time else None,
            'last_message': self.last_message_time.isoformat() if self.last_message_time else None,
            'uptime_seconds': uptime,
            'message_rate': round(message_rate, 2),
            'healthy': self.message_count > 0 and self.error_count == 0,
        }


class InfluxDBValidator:
    """Validates data in InfluxDB"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8086,
        username: str = 'zmq',
        password: str = 'zmq',
        database: str = 'tick'
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client: Optional[InfluxDBClient] = None
    
    def connect(self) -> bool:
        """Connect to InfluxDB"""
        try:
            self.client = InfluxDBClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database
            )
            
            # Test connection
            result = self.client.ping()
            if result:
                logger.info(f"✓ Connected to InfluxDB at {self.host}:{self.port}")
                return True
            else:
                logger.error("Failed to connect to InfluxDB")
                return False
        except Exception as e:
            logger.error(f"InfluxDB connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from InfluxDB"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def get_measurement_count(self, measurement: str) -> int:
        """Get count of points in a measurement"""
        try:
            query = f"SELECT COUNT(*) FROM {measurement}"
            result = self.client.query(query)
            
            for point in result.get_points():
                return point.get('count', 0)
            
            return 0
        except Exception as e:
            logger.error(f"Error querying {measurement}: {e}")
            return 0
    
    def get_latest_points(self, measurement: str, limit: int = 5) -> List[Dict]:
        """Get latest points from a measurement"""
        try:
            query = f"SELECT * FROM {measurement} ORDER BY time DESC LIMIT {limit}"
            result = self.client.query(query)
            
            return list(result.get_points())
        except Exception as e:
            logger.error(f"Error querying {measurement}: {e}")
            return []
    
    def validate_measurement(self, measurement: str, min_points: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """Validate that a measurement has data"""
        try:
            count = self.get_measurement_count(measurement)
            latest = self.get_latest_points(measurement, limit=1)
            
            status = {
                'measurement': measurement,
                'point_count': count,
                'has_data': count >= min_points,
                'latest_point': latest[0] if latest else None,
                'healthy': count >= min_points,
            }
            
            return status['healthy'], status
        except Exception as e:
            logger.error(f"Error validating {measurement}: {e}")
            return False, {'measurement': measurement, 'error': str(e)}
    
    def validate_all_measurements(self, measurements: List[str]) -> Dict[str, Any]:
        """Validate all measurements"""
        results = {}
        all_healthy = True
        
        for measurement in measurements:
            healthy, status = self.validate_measurement(measurement)
            results[measurement] = status
            if not healthy:
                all_healthy = False
        
        return {
            'all_healthy': all_healthy,
            'measurements': results,
            'timestamp': datetime.now().isoformat(),
        }


class MessageStreamValidator:
    """
    Validates complete message streaming pipeline:
    ZMQ Publishers → Subscribers → InfluxDB
    """
    
    def __init__(self, config_path: str = 'integration_config.json'):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.topic_monitors: Dict[str, TopicMonitor] = {}
        self.influxdb_validator: Optional[InfluxDBValidator] = None
        
        logger.info("Initialized MessageStreamValidator")
    
    def load_config(self) -> bool:
        """Load configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def validate_zmq_topics(self, duration: int = 10) -> Dict[str, Any]:
        """
        Validate that all ZMQ topics are streaming messages.
        
        Args:
            duration: How long to monitor each topic (seconds)
            
        Returns:
            Validation results
        """
        logger.info("=" * 70)
        logger.info("VALIDATING ZMQ MESSAGE STREAMING")
        logger.info("=" * 70)
        
        validation_topics = self.config.get('validation', {}).get('zmq_topics', [])
        
        results = {}
        all_healthy = True
        
        for topic in validation_topics:
            logger.info(f"Monitoring topic: {topic}")
            
            monitor = TopicMonitor(topic)
            if not monitor.connect():
                results[topic] = {
                    'healthy': False,
                    'error': 'Failed to connect to ZMQ'
                }
                all_healthy = False
                continue
            
            if not monitor.receive_messages(duration=duration):
                results[topic] = monitor.get_status()
                results[topic]['healthy'] = False
                all_healthy = False
                logger.warning(f"✗ No messages received on topic: {topic}")
                continue
            
            status = monitor.get_status()
            results[topic] = status
            
            if status['healthy']:
                logger.info(
                    f"✓ Topic '{topic}': {status['message_count']} messages, "
                    f"rate: {status['message_rate']} msg/sec"
                )
            else:
                logger.warning(f"✗ Topic '{topic}': {status['error_count']} errors")
                all_healthy = False
        
        logger.info("=" * 70)
        if all_healthy:
            logger.info("✓ ALL TOPICS STREAMING SUCCESSFULLY")
        else:
            logger.warning("⚠ SOME TOPICS HAVE ISSUES")
        logger.info("=" * 70)
        
        return {
            'all_healthy': all_healthy,
            'topics': results,
            'timestamp': datetime.now().isoformat(),
        }
    
    def validate_influxdb_data(self) -> Dict[str, Any]:
        """Validate that InfluxDB is receiving and storing data"""
        logger.info("=" * 70)
        logger.info("VALIDATING INFLUXDB DATA INGESTION")
        logger.info("=" * 70)
        
        influx_config = self.config.get('influxdb', {})
        
        self.influxdb_validator = InfluxDBValidator(
            host=influx_config.get('host', 'localhost'),
            port=influx_config.get('port', 8086),
            username=influx_config.get('username', 'zmq'),
            password=influx_config.get('password', 'zmq'),
            database=influx_config.get('database', 'tick')
        )
        
        if not self.influxdb_validator.connect():
            logger.error("Failed to connect to InfluxDB")
            return {'healthy': False, 'error': 'Connection failed'}
        
        try:
            measurements = list(influx_config.get('measurements', {}).keys())
            results = self.influxdb_validator.validate_all_measurements(measurements)
            
            for measurement, status in results['measurements'].items():
                if status['healthy']:
                    logger.info(
                        f"✓ {measurement}: {status['point_count']} points, "
                        f"latest: {status['latest_point']}"
                    )
                else:
                    logger.warning(f"✗ {measurement}: No data")
            
            logger.info("=" * 70)
            if results['all_healthy']:
                logger.info("✓ INFLUXDB DATA INGESTION SUCCESSFUL")
            else:
                logger.warning("⚠ SOME MEASUREMENTS HAVE NO DATA")
            logger.info("=" * 70)
            
            return results
        
        finally:
            self.influxdb_validator.disconnect()
    
    def full_validation(self, zmq_duration: int = 10) -> Dict[str, Any]:
        """
        Run complete validation of entire streaming pipeline.
        
        Returns:
            Comprehensive validation results
        """
        if not self.load_config():
            return {'error': 'Failed to load configuration'}
        
        zmq_results = self.validate_zmq_topics(duration=zmq_duration)
        
        time.sleep(2)
        
        influx_results = self.validate_influxdb_data()
        
        overall_healthy = (
            zmq_results.get('all_healthy', False) and
            influx_results.get('all_healthy', False)
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("OVERALL VALIDATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"ZMQ Streaming: {'✓ PASS' if zmq_results.get('all_healthy') else '✗ FAIL'}")
        logger.info(f"InfluxDB Data: {'✓ PASS' if influx_results.get('all_healthy') else '✗ FAIL'}")
        logger.info(f"Overall Status: {'✓ HEALTHY' if overall_healthy else '✗ UNHEALTHY'}")
        logger.info("=" * 70 + "\n")
        
        return {
            'overall_healthy': overall_healthy,
            'zmq': zmq_results,
            'influxdb': influx_results,
            'timestamp': datetime.now().isoformat(),
        }


def main():
    """Entry point for message validator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ZMQ Message Streaming Validator'
    )
    parser.add_argument(
        '--config',
        default='integration_config.json',
        help='Configuration file'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Duration to monitor ZMQ topics (seconds)'
    )
    parser.add_argument(
        'command',
        choices=['zmq', 'influxdb', 'full'],
        help='Validation to run'
    )
    
    args = parser.parse_args()
    
    validator = MessageStreamValidator(args.config)
    
    try:
        if args.command == 'zmq':
            validator.load_config()
            results = validator.validate_zmq_topics(duration=args.duration)
            return 0 if results.get('all_healthy') else 1
        
        elif args.command == 'influxdb':
            validator.load_config()
            results = validator.validate_influxdb_data()
            return 0 if results.get('all_healthy') else 1
        
        elif args.command == 'full':
            results = validator.full_validation(zmq_duration=args.duration)
            return 0 if results.get('overall_healthy') else 1
    
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
