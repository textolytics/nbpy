#!/usr/bin/env python3
"""
Automated migration generator for ZMQ microservices.
Converts all original services from python/scripts/zmq/ to nbpy.zmq module
with proper MessagePack serialization and standardized structure.
"""

import os
import sys
from pathlib import Path
import re

# Add nbpy to path
sys.path.insert(0, '/home/textolytics/nbpy')

def generate_publisher_wrapper(original_file, service_name):
    """Generate a wrapper publisher module that maintains original logic"""
    
    # Extract module name from original file
    original_module = Path(original_file).stem
    
    # Read original file to extract key patterns
    with open(original_file, 'r') as f:
        original_code = f.read()
    
    # Extract port
    port_match = re.search(r'port\s*=\s*["\'](\d+)["\']', original_code)
    port = port_match.group(1) if port_match else "5558"
    
    # Extract topic
    topic_match = re.search(r"topic\s*=\s*['\"]([^'\"]+)['\"]", original_code)
    topic = topic_match.group(1) if topic_match else service_name.replace('_', '_')
    
    # Create wrapper code
    wrapper = f'''"""
{service_name.upper()} Publisher Module
Auto-migrated from python/scripts/zmq/{Path(original_file).name}

This module wraps the original implementation while providing
nbpy.zmq framework integration with MessagePack serialization.
"""

import sys
import logging
from pathlib import Path

# Import framework components
from nbpy.zmq.base import BasePublisher
from nbpy.zmq.ports import PORT_REGISTRY
from nbpy.zmq.serialization import MessagePackCodec

logger = logging.getLogger(__name__)


class {service_name.replace('_', ' ').title().replace(' ', '')}Publisher(BasePublisher):
    """
    Publisher for {service_name.upper()}
    
    Original service: {Path(original_file).name}
    Port: {port}
    Topic: {topic}
    """
    
    def __init__(self):
        super().__init__(
            port={port},
            topic='{topic}',
            service_name='{service_name}'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized {service_name} Publisher on port {{self.port}}, topic: {{self.topic}}")
    
    def run(self):
        """Start the publisher - implement service-specific logic"""
        logger.info(f"{{self.service_name}} publisher started")
        
        try:
            # Import and run original service logic
            # This maintains backward compatibility with existing implementation
            from python.scripts.zmq.{original_module} import *
            
        except ImportError:
            logger.error(f"Could not import original module: {original_module}")
            logger.info("Please ensure python/scripts/zmq/ is in your PYTHONPATH")
            raise


def main():
    """Entry point for {service_name} publisher"""
    publisher = {service_name.replace('_', ' ').title().replace(' ', '')}Publisher()
    
    try:
        publisher.run()
    except KeyboardInterrupt:
        logger.info("{{publisher.service_name}} publisher interrupted by user")
        publisher.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"{{publisher.service_name}} publisher error: {{e}}", exc_info=True)
        publisher.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
'''
    
    return wrapper


def generate_subscriber_wrapper(original_file, service_name, backend_type='generic'):
    """Generate a wrapper subscriber module that maintains original logic"""
    
    original_module = Path(original_file).stem
    
    with open(original_file, 'r') as f:
        original_code = f.read()
    
    # Extract port - subscribers may connect to multiple ports
    ports = re.findall(r"socket\.connect\(['\"]tcp://[^:]+:(\d+)['\"]", original_code)
    port = ports[0] if ports else "5558"
    
    # Extract topic filter
    topic_match = re.search(r"setsockopt_string\(zmq\.SUBSCRIBE,\s*['\"]([^'\"]+)['\"]", original_code)
    topic = topic_match.group(1) if topic_match else service_name.replace('_', '_')
    
    # Determine base class based on backend
    if 'influxdb' in service_name.lower():
        base_class = "BaseInfluxDBSubscriber"
    elif 'pgsql' in service_name.lower() or 'postgresql' in service_name.lower():
        base_class = "BasePostgreSQLSubscriber"
    elif 'grakn' in service_name.lower():
        base_class = "BaseGraknSubscriber"
    elif 'kapacitor' in service_name.lower():
        base_class = "BaseKapacitorSubscriber"
    elif 'cuda' in service_name.lower():
        base_class = "BaseCUDASubscriber"
    elif 'pandas' in service_name.lower() or 'pd' in service_name.lower():
        base_class = "BasePandasSubscriber"
    else:
        base_class = "BaseSubscriber"
    
    wrapper = f'''"""
{service_name.upper()} Subscriber Module
Auto-migrated from python/scripts/zmq/{Path(original_file).name}

This module wraps the original implementation while providing
nbpy.zmq framework integration with MessagePack deserialization.
"""

import sys
import logging
from pathlib import Path

# Import framework components
from nbpy.zmq.base import BaseSubscriber, {base_class}
from nbpy.zmq.ports import PORT_REGISTRY
from nbpy.zmq.serialization import MessagePackCodec

logger = logging.getLogger(__name__)


class {service_name.replace('_', ' ').title().replace(' ', '')}Subscriber({base_class}):
    """
    Subscriber for {service_name.upper()}
    
    Original service: {Path(original_file).name}
    Connection port: {port}
    Topic filter: {topic}
    Backend type: {backend_type}
    """
    
    def __init__(self, connection_port={port}, topic_filter='{topic}'):
        super().__init__(
            connection_port=connection_port,
            topic_filter=topic_filter,
            service_name='{service_name}'
        )
        self.codec = MessagePackCodec()
        logger.info(f"Initialized {service_name} Subscriber on port {{self.connection_port}}, topic: {{self.topic_filter}}")
    
    def process_message(self, topic, data):
        """Process incoming message - implement service-specific logic"""
        try:
            # Deserialize MessagePack data
            message = self.codec.unpack(data)
            
            # Import and run original service logic
            from python.scripts.zmq.{original_module} import process_message
            
            # Call original processor
            process_message(topic, message)
            
        except Exception as e:
            logger.error(f"Error processing message: {{e}}", exc_info=True)
            raise
    
    def run(self):
        """Start the subscriber - implement service-specific logic"""
        logger.info(f"{{self.service_name}} subscriber started")
        
        try:
            # Import and run original service logic
            from python.scripts.zmq.{original_module} import run
            
            run()
            
        except ImportError:
            logger.error(f"Could not import original module: {original_module}")
            logger.info("Please ensure python/scripts/zmq/ is in your PYTHONPATH")
            # Fall back to base implementation
            super().run()


def main():
    """Entry point for {service_name} subscriber"""
    subscriber = {service_name.replace('_', ' ').title().replace(' ', '')}Subscriber()
    
    try:
        subscriber.run()
    except KeyboardInterrupt:
        logger.info("{{subscriber.service_name}} subscriber interrupted by user")
        subscriber.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"{{subscriber.service_name}} subscriber error: {{e}}", exc_info=True)
        subscriber.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
'''
    
    return wrapper


def main():
    """Generate all publisher and subscriber modules"""
    
    source_dir = Path('/home/textolytics/nbpy/python/scripts/zmq')
    pub_target_dir = Path('/home/textolytics/nbpy/nbpy/zmq/publishers')
    sub_target_dir = Path('/home/textolytics/nbpy/nbpy/zmq/subscribers')
    
    # Ensure target directories exist
    pub_target_dir.mkdir(parents=True, exist_ok=True)
    sub_target_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all publisher and subscriber files
    publishers = sorted(source_dir.glob('pub_*.py'))
    subscribers = sorted(source_dir.glob('sub_*.py'))
    
    print(f"Migrating {len(publishers)} publishers...")
    for pub_file in publishers:
        service_name = pub_file.stem.replace('pub_', '')
        wrapper_code = generate_publisher_wrapper(str(pub_file), service_name)
        
        output_file = pub_target_dir / f"{service_name}.py"
        with open(output_file, 'w') as f:
            f.write(wrapper_code)
        
        print(f"  ✓ {pub_file.name} → {output_file.name}")
    
    print(f"\nMigrating {len(subscribers)} subscribers...")
    for sub_file in subscribers:
        service_name = sub_file.stem.replace('sub_', '')
        wrapper_code = generate_subscriber_wrapper(str(sub_file), service_name)
        
        output_file = sub_target_dir / f"{service_name}.py"
        with open(output_file, 'w') as f:
            f.write(wrapper_code)
        
        print(f"  ✓ {sub_file.name} → {output_file.name}")
    
    print(f"\n✓ Migration complete! Total: {len(publishers) + len(subscribers)} services")
    print(f"Publishers: {pub_target_dir}")
    print(f"Subscribers: {sub_target_dir}")


if __name__ == '__main__':
    main()
