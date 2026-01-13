#!/usr/bin/env python3
"""
ZMQ Microservices Lifecycle Manager

Manages the startup, monitoring, and graceful shutdown of all ZMQ publishers and subscribers.
Handles:
- Process lifecycle management
- Signal handlers for graceful shutdown
- Health checks and monitoring
- Logging and error handling
"""

import json
import logging
import os
import signal
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Thread, Event
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/service_manager.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a single service"""
    name: str
    module: str
    class_name: str
    port: int
    topic: str
    enabled: bool = True
    description: str = ""
    extra_args: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'module': self.module,
            'class': self.class_name,
            'port': self.port,
            'topic': self.topic,
            'enabled': self.enabled,
            'description': self.description,
            'args': self.extra_args,
        }


@dataclass
class ServiceProcess:
    """Running service process"""
    config: ServiceConfig
    process: Optional[subprocess.Popen] = None
    start_time: Optional[datetime] = None
    stop_event: Event = field(default_factory=Event)
    message_count: int = 0
    error_count: int = 0
    
    def is_running(self) -> bool:
        """Check if process is still running"""
        return self.process is not None and self.process.poll() is None
    
    def uptime_seconds(self) -> float:
        """Get service uptime in seconds"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0


class BaseServiceRunner(ABC):
    """Base class for service runners (Publisher/Subscriber)"""
    
    def __init__(self, config: ServiceConfig, python_executable: str):
        self.config = config
        self.python_executable = python_executable
        self.process: Optional[subprocess.Popen] = None
        self.stop_event = Event()
    
    def _build_command(self) -> List[str]:
        """Build the command to run the service"""
        command = [
            self.python_executable,
            "-m",
            self.config.module,
        ]
        command.extend(self.config.extra_args)
        return command
    
    def start(self) -> bool:
        """Start the service process"""
        try:
            command = self._build_command()
            logger.info(f"Starting {self.config.name}: {' '.join(command)}")
            
            log_file = Path(f"logs/{self.config.name}.log")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, 'a') as f:
                self.process = subprocess.Popen(
                    command,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            # Give process time to start
            time.sleep(0.5)
            
            if self.process.poll() is None:
                logger.info(f"✓ {self.config.name} started (PID: {self.process.pid})")
                return True
            else:
                logger.error(f"✗ {self.config.name} failed to start")
                return False
        except Exception as e:
            logger.error(f"Failed to start {self.config.name}: {e}")
            return False
    
    def stop(self, timeout: int = 10) -> bool:
        """Stop the service process gracefully"""
        if not self.process:
            return True
        
        try:
            logger.info(f"Stopping {self.config.name} (PID: {self.process.pid})...")
            self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=timeout)
                logger.info(f"✓ {self.config.name} stopped gracefully")
                return True
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {self.config.name}...")
                self.process.kill()
                self.process.wait()
                logger.warning(f"✗ {self.config.name} force killed")
                return False
        except Exception as e:
            logger.error(f"Error stopping {self.config.name}: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if process is running"""
        return self.process is not None and self.process.poll() is None
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'name': self.config.name,
            'port': self.config.port,
            'topic': self.config.topic,
            'enabled': self.config.enabled,
            'running': self.is_running(),
            'pid': self.process.pid if self.process else None,
        }


class ZMQServiceManager:
    """
    Manages lifecycle of all ZMQ publishers and subscribers.
    
    Responsibilities:
    - Load configuration from JSON
    - Start services in correct order
    - Monitor service health
    - Graceful shutdown on signals
    - Provide status and logging
    """
    
    def __init__(self, config_path: str, python_executable: str = sys.executable):
        self.config_path = Path(config_path)
        self.python_executable = python_executable
        self.config_data: Dict[str, Any] = {}
        self.publishers: Dict[str, BaseServiceRunner] = {}
        self.subscribers: Dict[str, BaseServiceRunner] = {}
        self.running = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Initialized ZMQServiceManager")
    
    def load_config(self) -> bool:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _create_publishers(self) -> bool:
        """Create publisher service runners"""
        try:
            publishers = self.config_data.get('publishers', [])
            for pub_config in publishers:
                if not pub_config.get('enabled', True):
                    continue
                
                config = ServiceConfig(
                    name=pub_config['name'],
                    module=pub_config['module'],
                    class_name=pub_config.get('class', ''),
                    port=pub_config['port'],
                    topic=pub_config['topic'],
                    enabled=pub_config.get('enabled', True),
                    description=pub_config.get('description', ''),
                )
                self.publishers[config.name] = BaseServiceRunner(config, self.python_executable)
            
            logger.info(f"Created {len(self.publishers)} publisher service(s)")
            return True
        except Exception as e:
            logger.error(f"Failed to create publishers: {e}")
            return False
    
    def _create_subscribers(self) -> bool:
        """Create subscriber service runners"""
        try:
            subscribers = self.config_data.get('subscribers', [])
            for sub_config in subscribers:
                if not sub_config.get('enabled', True):
                    continue
                
                config = ServiceConfig(
                    name=sub_config['name'],
                    module=sub_config['module'],
                    class_name=sub_config.get('class', ''),
                    port=sub_config['port'],
                    topic=sub_config.get('subscribe_to', ''),
                    enabled=sub_config.get('enabled', True),
                    description=sub_config.get('description', ''),
                )
                self.subscribers[config.name] = BaseServiceRunner(config, self.python_executable)
            
            logger.info(f"Created {len(self.subscribers)} subscriber service(s)")
            return True
        except Exception as e:
            logger.error(f"Failed to create subscribers: {e}")
            return False
    
    def start_publishers(self) -> bool:
        """Start all enabled publishers"""
        logger.info("Starting publishers...")
        success = True
        
        for name, runner in self.publishers.items():
            if not runner.start():
                success = False
            time.sleep(0.5)
        
        return success
    
    def start_subscribers(self) -> bool:
        """Start all enabled subscribers"""
        logger.info("Starting subscribers...")
        success = True
        
        for name, runner in self.subscribers.items():
            if not runner.start():
                success = False
            time.sleep(0.5)
        
        return success
    
    def stop_subscribers(self, timeout: int = 10) -> bool:
        """Stop all subscribers"""
        logger.info("Stopping subscribers...")
        success = True
        
        for name, runner in self.subscribers.items():
            if not runner.stop(timeout):
                success = False
        
        return success
    
    def stop_publishers(self, timeout: int = 10) -> bool:
        """Stop all publishers"""
        logger.info("Stopping publishers...")
        success = True
        
        for name, runner in self.publishers.items():
            if not runner.stop(timeout):
                success = False
        
        return success
    
    def start_all(self) -> bool:
        """Start all services in correct order"""
        logger.info("=" * 70)
        logger.info("STARTING ALL ZMQ SERVICES")
        logger.info("=" * 70)
        
        self.running = True
        
        if not self.load_config():
            return False
        
        if not self._create_publishers() or not self._create_subscribers():
            return False
        
        if not self.start_publishers():
            self.stop_publishers()
            return False
        
        logger.info("Waiting 2 seconds before starting subscribers...")
        time.sleep(2)
        
        if not self.start_subscribers():
            self.stop_all()
            return False
        
        logger.info("=" * 70)
        logger.info("ALL SERVICES STARTED SUCCESSFULLY")
        logger.info("=" * 70)
        
        return True
    
    def stop_all(self, timeout: int = 30) -> bool:
        """Stop all services gracefully"""
        logger.info("=" * 70)
        logger.info("STOPPING ALL ZMQ SERVICES")
        logger.info("=" * 70)
        
        self.running = False
        
        # Stop subscribers first, then publishers
        self.stop_subscribers(timeout // 2)
        time.sleep(1)
        self.stop_publishers(timeout // 2)
        
        logger.info("=" * 70)
        logger.info("ALL SERVICES STOPPED")
        logger.info("=" * 70)
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            'running': self.running,
            'publishers': {
                name: runner.get_status()
                for name, runner in self.publishers.items()
            },
            'subscribers': {
                name: runner.get_status()
                for name, runner in self.subscribers.items()
            },
            'timestamp': datetime.now().isoformat(),
        }
    
    def print_status(self):
        """Print formatted status of all services"""
        status = self.get_status()
        
        print("\n" + "=" * 70)
        print("PUBLISHERS")
        print("=" * 70)
        for name, info in status['publishers'].items():
            state = "✓ RUNNING" if info['running'] else "✗ STOPPED"
            print(f"  {name:30} {state:15} (PID: {info['pid']}, Port: {info['port']})")
        
        print("\n" + "=" * 70)
        print("SUBSCRIBERS")
        print("=" * 70)
        for name, info in status['subscribers'].items():
            state = "✓ RUNNING" if info['running'] else "✗ STOPPED"
            print(f"  {name:30} {state:15} (PID: {info['pid']}, Port: {info['port']})")
        
        print("=" * 70 + "\n")
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        self.stop_all()
        sys.exit(0)
    
    def monitor(self, interval: int = 30):
        """Monitor service health and restart failed services"""
        logger.info(f"Starting health monitor (check interval: {interval}s)")
        
        while self.running:
            try:
                status = self.get_status()
                
                for name, info in status['publishers'].items():
                    if not info['running']:
                        logger.warning(f"Publisher {name} is not running, restarting...")
                        if name in self.publishers:
                            self.publishers[name].start()
                
                for name, info in status['subscribers'].items():
                    if not info['running']:
                        logger.warning(f"Subscriber {name} is not running, restarting...")
                        if name in self.subscribers:
                            self.subscribers[name].start()
                
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)


def main():
    """Entry point for service manager"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ZMQ Microservices Lifecycle Manager'
    )
    parser.add_argument(
        '--config',
        default='integration_config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status', 'monitor'],
        help='Command to execute'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Shutdown timeout in seconds'
    )
    
    args = parser.parse_args()
    
    manager = ZMQServiceManager(args.config)
    
    if args.command == 'start':
        success = manager.start_all()
        sys.exit(0 if success else 1)
    
    elif args.command == 'stop':
        success = manager.stop_all(timeout=args.timeout)
        sys.exit(0 if success else 1)
    
    elif args.command == 'restart':
        manager.stop_all(timeout=args.timeout)
        time.sleep(2)
        success = manager.start_all()
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        manager.print_status()
        sys.exit(0)
    
    elif args.command == 'monitor':
        manager.load_config()
        manager._create_publishers()
        manager._create_subscribers()
        manager.monitor()


if __name__ == '__main__':
    main()
