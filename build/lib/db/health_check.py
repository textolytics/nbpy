#!/usr/bin/env python3
"""
NBPY Health Check and System Monitoring

Continuous monitoring of:
- Docker container health
- ZMQ publisher/subscriber status
- Message flow rates
- InfluxDB data ingestion
- Grafana dashboard status
- System resource usage
"""

import json
import logging
import time
import subprocess
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from threading import Thread, Event
from collections import defaultdict
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/health_check.log')
    ]
)
logger = logging.getLogger(__name__)


class HealthStatus:
    """Represents health status of a component"""
    
    def __init__(self, name: str):
        self.name = name
        self.healthy = False
        self.message = ""
        self.last_check = None
        self.check_count = 0
        self.fail_count = 0
    
    def mark_healthy(self, message: str = ""):
        self.healthy = True
        self.message = message
        self.last_check = datetime.now()
        self.check_count += 1
    
    def mark_unhealthy(self, message: str = ""):
        self.healthy = False
        self.message = message
        self.last_check = datetime.now()
        self.check_count += 1
        self.fail_count += 1
    
    def uptime_percent(self) -> float:
        if self.check_count == 0:
            return 0
        return ((self.check_count - self.fail_count) / self.check_count) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'healthy': self.healthy,
            'message': self.message,
            'uptime_percent': self.uptime_percent(),
            'check_count': self.check_count,
            'fail_count': self.fail_count,
            'last_check': self.last_check.isoformat() if self.last_check else None,
        }


class DockerHealthCheck:
    """Check Docker container health"""
    
    def __init__(self):
        self.influxdb_status = HealthStatus("influxdb_container")
        self.grafana_status = HealthStatus("grafana_container")
    
    def check_containers(self) -> bool:
        """Check Docker containers are running"""
        try:
            result = subprocess.run(
                ['docker-compose', 'ps', '--services', '--filter', 'status=running'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            running_services = result.stdout.strip().split('\n')
            
            # Check InfluxDB
            if 'influxdb' in running_services or 'nbpy-influxdb' in running_services:
                if self._check_influxdb_health():
                    self.influxdb_status.mark_healthy("InfluxDB container running and healthy")
                else:
                    self.influxdb_status.mark_unhealthy("InfluxDB container not responding")
            else:
                self.influxdb_status.mark_unhealthy("InfluxDB container not running")
            
            # Check Grafana
            if 'grafana' in running_services or 'nbpy-grafana' in running_services:
                if self._check_grafana_health():
                    self.grafana_status.mark_healthy("Grafana container running and healthy")
                else:
                    self.grafana_status.mark_unhealthy("Grafana container not responding")
            else:
                self.grafana_status.mark_unhealthy("Grafana container not running")
            
            return self.influxdb_status.healthy and self.grafana_status.healthy
        
        except Exception as e:
            logger.error(f"Error checking containers: {e}")
            self.influxdb_status.mark_unhealthy(f"Error: {e}")
            self.grafana_status.mark_unhealthy(f"Error: {e}")
            return False
    
    def _check_influxdb_health(self) -> bool:
        """Check InfluxDB health endpoint"""
        try:
            response = requests.get(
                'http://localhost:8086/ping',
                timeout=5
            )
            return response.status_code == 204
        except Exception as e:
            logger.debug(f"InfluxDB health check failed: {e}")
            return False
    
    def _check_grafana_health(self) -> bool:
        """Check Grafana health endpoint"""
        try:
            response = requests.get(
                'http://localhost:3000/api/health',
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Grafana health check failed: {e}")
            return False


class ZMQHealthCheck:
    """Check ZMQ publisher/subscriber health"""
    
    def __init__(self):
        self.publisher_statuses: Dict[str, HealthStatus] = {}
        self.subscriber_statuses: Dict[str, HealthStatus] = {}
    
    def check_services(self, config_path: str = 'integration_config.json') -> bool:
        """Check ZMQ services from configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check publishers
            all_healthy = True
            for pub in config.get('publishers', []):
                if pub.get('enabled', True):
                    name = pub['name']
                    port = pub['port']
                    
                    if name not in self.publisher_statuses:
                        self.publisher_statuses[name] = HealthStatus(f"publisher_{name}")
                    
                    if self._check_port_listening(port):
                        self.publisher_statuses[name].mark_healthy(f"Listening on port {port}")
                    else:
                        self.publisher_statuses[name].mark_unhealthy(f"Not listening on port {port}")
                        all_healthy = False
            
            # Check subscribers
            for sub in config.get('subscribers', []):
                if sub.get('enabled', True):
                    name = sub['name']
                    port = sub['port']
                    
                    if name not in self.subscriber_statuses:
                        self.subscriber_statuses[name] = HealthStatus(f"subscriber_{name}")
                    
                    if self._check_port_listening(port):
                        self.subscriber_statuses[name].mark_healthy(f"Listening on port {port}")
                    else:
                        self.subscriber_statuses[name].mark_unhealthy(f"Not listening on port {port}")
                        all_healthy = False
            
            return all_healthy
        
        except Exception as e:
            logger.error(f"Error checking ZMQ services: {e}")
            return False
    
    def _check_port_listening(self, port: int) -> bool:
        """Check if port is listening"""
        try:
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return f":{port}" in result.stdout
        except Exception as e:
            logger.debug(f"Port check failed: {e}")
            return False


class DataIngestionHealthCheck:
    """Check InfluxDB data ingestion"""
    
    def __init__(self):
        self.measurement_statuses: Dict[str, HealthStatus] = {}
        self.last_point_counts: Dict[str, int] = {}
    
    def check_influxdb(self, config_path: str = 'integration_config.json') -> bool:
        """Check InfluxDB data ingestion"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            influx_config = config.get('influxdb', {})
            measurements = influx_config.get('measurements', {})
            
            all_healthy = True
            
            for measurement_name in measurements.keys():
                if measurement_name not in self.measurement_statuses:
                    self.measurement_statuses[measurement_name] = HealthStatus(
                        f"influxdb_{measurement_name}"
                    )
                
                # Check if measurement has recent data
                count = self._get_measurement_count(measurement_name, influx_config)
                
                if count > 0:
                    last_count = self.last_point_counts.get(measurement_name, 0)
                    
                    if count > last_count:
                        msg = f"{count} points, growing ({count - last_count} new)"
                        self.measurement_statuses[measurement_name].mark_healthy(msg)
                    else:
                        msg = f"{count} points, not growing"
                        self.measurement_statuses[measurement_name].mark_unhealthy(msg)
                        all_healthy = False
                    
                    self.last_point_counts[measurement_name] = count
                else:
                    self.measurement_statuses[measurement_name].mark_unhealthy("No data")
                    all_healthy = False
            
            return all_healthy
        
        except Exception as e:
            logger.error(f"Error checking InfluxDB: {e}")
            return False
    
    def _get_measurement_count(self, measurement: str, influx_config: Dict) -> int:
        """Get count of points in measurement"""
        try:
            from influxdb import InfluxDBClient
            
            client = InfluxDBClient(
                host=influx_config.get('host', 'localhost'),
                port=influx_config.get('port', 8086),
                username=influx_config.get('username', 'zmq'),
                password=influx_config.get('password', 'zmq'),
                database=influx_config.get('database', 'tick')
            )
            
            query = f"SELECT COUNT(*) FROM {measurement}"
            result = client.query(query)
            
            for point in result.get_points():
                return point.get('count', 0)
            
            return 0
        
        except Exception as e:
            logger.debug(f"Error querying {measurement}: {e}")
            return 0


class SystemHealthMonitor:
    """Unified health monitoring system"""
    
    def __init__(self, config_path: str = 'integration_config.json', interval: int = 30):
        self.config_path = config_path
        self.interval = interval
        self.running = False
        self.stop_event = Event()
        
        self.docker_check = DockerHealthCheck()
        self.zmq_check = ZMQHealthCheck()
        self.data_check = DataIngestionHealthCheck()
        
        logger.info(f"Initialized SystemHealthMonitor (interval: {interval}s)")
    
    def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("=" * 70)
        logger.info("RUNNING SYSTEM HEALTH CHECKS")
        logger.info("=" * 70)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_healthy': True,
            'docker': {},
            'zmq': {},
            'data': {}
        }
        
        # Docker checks
        docker_healthy = self.docker_check.check_containers()
        results['docker'] = {
            'healthy': docker_healthy,
            'influxdb': self.docker_check.influxdb_status.to_dict(),
            'grafana': self.docker_check.grafana_status.to_dict(),
        }
        
        if not docker_healthy:
            results['overall_healthy'] = False
        
        # ZMQ checks (only if Docker healthy)
        if docker_healthy:
            zmq_healthy = self.zmq_check.check_services(self.config_path)
            results['zmq'] = {
                'healthy': zmq_healthy,
                'publishers': {
                    name: status.to_dict()
                    for name, status in self.zmq_check.publisher_statuses.items()
                },
                'subscribers': {
                    name: status.to_dict()
                    for name, status in self.zmq_check.subscriber_statuses.items()
                }
            }
            
            if not zmq_healthy:
                results['overall_healthy'] = False
            
            # Data ingestion checks
            data_healthy = self.data_check.check_influxdb(self.config_path)
            results['data'] = {
                'healthy': data_healthy,
                'measurements': {
                    name: status.to_dict()
                    for name, status in self.data_check.measurement_statuses.items()
                }
            }
            
            if not data_healthy:
                results['overall_healthy'] = False
        
        self._print_results(results)
        
        return results
    
    def _print_results(self, results: Dict[str, Any]):
        """Print formatted results"""
        logger.info("\n" + "=" * 70)
        logger.info("DOCKER CONTAINERS")
        logger.info("=" * 70)
        
        for name, status in [
            ("InfluxDB", results['docker']['influxdb']),
            ("Grafana", results['docker']['grafana'])
        ]:
            health_icon = "✓" if status['healthy'] else "✗"
            uptime = f"{status['uptime_percent']:.1f}%"
            logger.info(f"{health_icon} {name:15} {status['message']:40} {uptime}")
        
        if results['zmq']:
            logger.info("\n" + "=" * 70)
            logger.info("ZMQ PUBLISHERS")
            logger.info("=" * 70)
            
            for name, status in results['zmq'].get('publishers', {}).items():
                health_icon = "✓" if status['healthy'] else "✗"
                uptime = f"{status['uptime_percent']:.1f}%"
                logger.info(f"{health_icon} {name:30} {status['message']:25} {uptime}")
            
            logger.info("\n" + "=" * 70)
            logger.info("ZMQ SUBSCRIBERS")
            logger.info("=" * 70)
            
            for name, status in results['zmq'].get('subscribers', {}).items():
                health_icon = "✓" if status['healthy'] else "✗"
                uptime = f"{status['uptime_percent']:.1f}%"
                logger.info(f"{health_icon} {name:30} {status['message']:25} {uptime}")
            
            logger.info("\n" + "=" * 70)
            logger.info("DATA INGESTION")
            logger.info("=" * 70)
            
            for name, status in results['data'].get('measurements', {}).items():
                health_icon = "✓" if status['healthy'] else "✗"
                uptime = f"{status['uptime_percent']:.1f}%"
                logger.info(f"{health_icon} {name:30} {status['message']:25} {uptime}")
        
        logger.info("\n" + "=" * 70)
        overall_status = "✓ HEALTHY" if results['overall_healthy'] else "✗ UNHEALTHY"
        logger.info(f"OVERALL STATUS: {overall_status}")
        logger.info("=" * 70 + "\n")
    
    def monitor(self):
        """Continuous health monitoring"""
        self.running = True
        logger.info(f"Starting continuous health monitoring (interval: {self.interval}s)")
        
        while self.running and not self.stop_event.is_set():
            try:
                self.check_all()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                logger.info("Health monitoring stopped by user")
                self.stop()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.interval)
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.stop_event.set()
        logger.info("Health monitoring stopped")


def main():
    """Entry point for health check"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='NBPY System Health Monitor'
    )
    parser.add_argument(
        '--config',
        default='integration_config.json',
        help='Configuration file'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Health check interval in seconds'
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='check',
        choices=['check', 'monitor'],
        help='Command: check (once) or monitor (continuous)'
    )
    
    args = parser.parse_args()
    
    monitor = SystemHealthMonitor(args.config, args.interval)
    
    if args.command == 'check':
        results = monitor.check_all()
        return 0 if results['overall_healthy'] else 1
    
    elif args.command == 'monitor':
        try:
            monitor.monitor()
        except KeyboardInterrupt:
            logger.info("\nMonitoring interrupted")
            return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
