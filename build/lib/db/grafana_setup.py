#!/usr/bin/env python3
"""
Grafana Dashboard Provisioning

Automatically creates and provisions Grafana dashboards for monitoring
ZMQ message topics and InfluxDB data streams.
"""

import json
import logging
import time
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/grafana_setup.log')
    ]
)
logger = logging.getLogger(__name__)


class GrafanaClient:
    """Grafana API client for dashboard provisioning"""
    
    def __init__(
        self,
        url: str = 'http://localhost:3000',
        username: str = 'admin',
        password: str = 'admin123',
        api_key: Optional[str] = None
    ):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        else:
            self.session.auth = (username, password)
        
        logger.info(f"Initialized GrafanaClient for {url}")
    
    def health_check(self) -> bool:
        """Check if Grafana is healthy"""
        try:
            response = self.session.get(f"{self.url}/api/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def wait_for_health(self, timeout: int = 60, interval: int = 2) -> bool:
        """Wait for Grafana to be healthy"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.health_check():
                logger.info("✓ Grafana is healthy")
                return True
            
            logger.info(f"Waiting for Grafana... ({int(time.time() - start_time)}s)")
            time.sleep(interval)
        
        logger.error("Grafana health check timeout")
        return False
    
    def get_datasources(self) -> List[Dict[str, Any]]:
        """Get all datasources"""
        try:
            response = self.session.get(f"{self.url}/api/datasources")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get datasources: {e}")
            return []
    
    def create_datasource(
        self,
        name: str,
        datasource_type: str = 'influxdb',
        url: str = 'http://influxdb:8086',
        database: str = 'tick',
        username: str = 'zmq',
        password: str = 'zmq',
        is_default: bool = True
    ) -> bool:
        """Create a datasource"""
        try:
            # Check if datasource already exists
            existing = [ds for ds in self.get_datasources() if ds.get('name') == name]
            if existing:
                logger.info(f"✓ Datasource '{name}' already exists")
                return True
            
            payload = {
                'name': name,
                'type': datasource_type,
                'url': url,
                'access': 'proxy',
                'isDefault': is_default,
                'jsonData': {
                    'dbName': database
                },
                'secureJsonData': {
                    'password': password
                },
                'secureJsonFields': {
                    'password': True
                }
            }
            
            # Add username if provided
            if username:
                payload['jsonData']['username'] = username
            
            logger.info(f"Creating datasource: {name}")
            response = self.session.post(
                f"{self.url}/api/datasources",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"✓ Datasource '{name}' created")
            return True
        except Exception as e:
            logger.error(f"Failed to create datasource: {e}")
            return False
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict]:
        """Get dashboard by UID"""
        try:
            response = self.session.get(f"{self.url}/api/dashboards/uid/{dashboard_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get dashboard: {e}")
            return None
    
    def create_dashboard(
        self,
        title: str,
        dashboard_json: Dict[str, Any],
        overwrite: bool = True
    ) -> bool:
        """Create or update a dashboard"""
        try:
            # Add metadata
            dashboard_json['title'] = title
            dashboard_json['timezone'] = 'browser'
            dashboard_json['schemaVersion'] = 16
            dashboard_json['version'] = 0
            
            payload = {
                'dashboard': dashboard_json,
                'overwrite': overwrite
            }
            
            logger.info(f"Creating dashboard: {title}")
            response = self.session.post(
                f"{self.url}/api/dashboards/db",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✓ Dashboard '{title}' created (ID: {result.get('id')})")
            return True
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return False
    
    def delete_dashboard(self, dashboard_uid: str) -> bool:
        """Delete dashboard by UID"""
        try:
            response = self.session.delete(f"{self.url}/api/dashboards/uid/{dashboard_uid}")
            response.raise_for_status()
            logger.info(f"✓ Dashboard '{dashboard_uid}' deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete dashboard: {e}")
            return False


class DashboardBuilder:
    """Builds Grafana dashboard JSON"""
    
    @staticmethod
    def create_graph_panel(
        title: str,
        measurement: str,
        field: str,
        panel_id: int,
        grid_pos: Dict[str, int]
    ) -> Dict[str, Any]:
        """Create a graph panel"""
        return {
            'id': panel_id,
            'type': 'graph',
            'title': title,
            'datasource': 'InfluxDB',
            'targets': [
                {
                    'expr': '',
                    'refId': 'A',
                    'measurement': measurement,
                    'select': [
                        [
                            {'type': 'field', 'params': [field]},
                            {'type': 'mean', 'params': []}
                        ]
                    ],
                    'orderByTime': 'ASC',
                    'policy': 'default',
                    'resultFormat': 'time_series',
                    'tags': [],
                    'groupBy': [
                        {'type': 'time', 'params': ['$__interval']}
                    ]
                }
            ],
            'gridPos': grid_pos,
            'yaxes': [
                {'format': 'short', 'label': 'Value', 'logBase': 1},
                {'format': 'short', 'logBase': 1}
            ],
            'xaxis': {'mode': 'time'},
            'options': {}
        }
    
    @staticmethod
    def create_stat_panel(
        title: str,
        measurement: str,
        field: str,
        panel_id: int,
        grid_pos: Dict[str, int]
    ) -> Dict[str, Any]:
        """Create a stat panel"""
        return {
            'id': panel_id,
            'type': 'stat',
            'title': title,
            'datasource': 'InfluxDB',
            'targets': [
                {
                    'measurement': measurement,
                    'select': [
                        [
                            {'type': 'field', 'params': [field]},
                            {'type': 'last', 'params': []}
                        ]
                    ],
                    'orderByTime': 'ASC',
                    'policy': 'default',
                    'resultFormat': 'time_series',
                    'tags': []
                }
            ],
            'gridPos': grid_pos,
            'options': {
                'orientation': 'auto',
                'textMode': 'auto',
                'colorMode': 'background',
                'graphMode': 'area'
            }
        }
    
    @staticmethod
    def create_table_panel(
        title: str,
        measurement: str,
        panel_id: int,
        grid_pos: Dict[str, int]
    ) -> Dict[str, Any]:
        """Create a table panel"""
        return {
            'id': panel_id,
            'type': 'table',
            'title': title,
            'datasource': 'InfluxDB',
            'targets': [
                {
                    'measurement': measurement,
                    'select': [[{'type': 'field', 'params': ['*']}]],
                    'orderByTime': 'DESC',
                    'policy': 'default',
                    'resultFormat': 'table',
                    'tags': []
                }
            ],
            'gridPos': grid_pos,
            'options': {}
        }
    
    @staticmethod
    def create_dashboard(
        title: str,
        measurement: str,
        fields: List[str] = None
    ) -> Dict[str, Any]:
        """Create complete dashboard for a measurement"""
        if fields is None:
            fields = ['value', 'last_trade_price', 'bid', 'ask']
        
        # Filter fields that are likely to exist
        default_fields = fields[:2] if fields else ['value']
        
        panels = []
        panel_id = 1
        
        # Row 1: Time series graphs
        for idx, field in enumerate(default_fields):
            grid_pos = {
                'h': 8,
                'w': 12,
                'x': (idx % 2) * 12,
                'y': 0 if idx < 2 else 8
            }
            
            panel = DashboardBuilder.create_graph_panel(
                title=f"{measurement} - {field}",
                measurement=measurement,
                field=field,
                panel_id=panel_id,
                grid_pos=grid_pos
            )
            panels.append(panel)
            panel_id += 1
        
        # Row 2: Latest values as stats
        grid_pos = {
            'h': 4,
            'w': 6,
            'x': 0,
            'y': 16
        }
        
        for idx, field in enumerate(default_fields[:2]):
            grid_pos['x'] = idx * 6
            
            panel = DashboardBuilder.create_stat_panel(
                title=f"Latest {field}",
                measurement=measurement,
                field=field,
                panel_id=panel_id,
                grid_pos=grid_pos
            )
            panels.append(panel)
            panel_id += 1
        
        # Row 3: Table of latest data
        grid_pos = {
            'h': 8,
            'w': 24,
            'x': 0,
            'y': 20
        }
        
        panel = DashboardBuilder.create_table_panel(
            title=f"{measurement} - Latest Data",
            measurement=measurement,
            panel_id=panel_id,
            grid_pos=grid_pos
        )
        panels.append(panel)
        
        return {
            'uid': measurement.lower(),
            'title': title,
            'description': f'Real-time monitoring of {measurement} data stream',
            'tags': ['zmq', 'influxdb', 'realtime', measurement.lower()],
            'timezone': 'browser',
            'panels': panels,
            'time': {'from': 'now-1h', 'to': 'now'},
            'timepicker': {},
            'refresh': '5s'
        }


class GrafanaSetup:
    """Orchestrates Grafana setup and dashboard provisioning"""
    
    def __init__(self, config_path: str = 'integration_config.json'):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.client: Optional[GrafanaClient] = None
    
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
    
    def setup_datasource(self) -> bool:
        """Setup InfluxDB datasource"""
        try:
            influx_config = self.config.get('influxdb', {})
            
            logger.info("=" * 70)
            logger.info("SETTING UP GRAFANA DATASOURCE")
            logger.info("=" * 70)
            
            success = self.client.create_datasource(
                name='InfluxDB',
                database=influx_config.get('database', 'tick'),
                username=influx_config.get('username', 'zmq'),
                password=influx_config.get('password', 'zmq'),
                url=f"http://influxdb:8086"
            )
            
            if success:
                logger.info("=" * 70)
                logger.info("✓ DATASOURCE CONFIGURED")
                logger.info("=" * 70)
            
            return success
        except Exception as e:
            logger.error(f"Failed to setup datasource: {e}")
            return False
    
    def create_dashboards(self) -> bool:
        """Create dashboards for all measurements"""
        try:
            influx_config = self.config.get('influxdb', {})
            measurements = influx_config.get('measurements', {})
            
            logger.info("=" * 70)
            logger.info("CREATING GRAFANA DASHBOARDS")
            logger.info("=" * 70)
            
            success = True
            
            for measurement_name, measurement_config in measurements.items():
                fields = measurement_config.get('fields', [])
                
                dashboard_json = DashboardBuilder.create_dashboard(
                    title=f"{measurement_name.upper()} Stream",
                    measurement=measurement_name,
                    fields=fields
                )
                
                if not self.client.create_dashboard(
                    title=f"{measurement_name.upper()} Stream",
                    dashboard_json=dashboard_json
                ):
                    success = False
                
                time.sleep(0.5)
            
            logger.info("=" * 70)
            if success:
                logger.info("✓ DASHBOARDS CREATED SUCCESSFULLY")
            else:
                logger.warning("⚠ SOME DASHBOARDS FAILED")
            logger.info("=" * 70)
            
            return success
        except Exception as e:
            logger.error(f"Failed to create dashboards: {e}")
            return False
    
    def setup(self) -> bool:
        """Run complete Grafana setup"""
        if not self.load_config():
            return False
        
        grafana_config = self.config.get('docker', {}).get('services', {}).get('grafana', {})
        
        self.client = GrafanaClient(
            url='http://localhost:3000',
            username=grafana_config.get('admin_user', 'admin'),
            password=grafana_config.get('admin_password', 'admin123')
        )
        
        logger.info("Waiting for Grafana to be healthy...")
        if not self.client.wait_for_health():
            return False
        
        if not self.setup_datasource():
            return False
        
        time.sleep(2)
        
        if not self.create_dashboards():
            return False
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ GRAFANA SETUP COMPLETE")
        logger.info("=" * 70)
        logger.info("Access Grafana at: http://localhost:3000")
        logger.info("Username: admin")
        logger.info("Password: admin123")
        logger.info("=" * 70 + "\n")
        
        return True


def main():
    """Entry point for Grafana setup"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Grafana Dashboard Provisioning'
    )
    parser.add_argument(
        '--config',
        default='integration_config.json',
        help='Configuration file'
    )
    parser.add_argument(
        'command',
        choices=['setup', 'datasource', 'dashboards'],
        help='Setup command'
    )
    
    args = parser.parse_args()
    
    setup = GrafanaSetup(args.config)
    
    if args.command == 'setup':
        success = setup.setup()
        return 0 if success else 1
    
    elif args.command == 'datasource':
        if not setup.load_config():
            return 1
        
        grafana_config = setup.config.get('docker', {}).get('services', {}).get('grafana', {})
        setup.client = GrafanaClient(
            url='http://localhost:3000',
            username=grafana_config.get('admin_user', 'admin'),
            password=grafana_config.get('admin_password', 'admin123')
        )
        
        success = setup.setup_datasource()
        return 0 if success else 1
    
    elif args.command == 'dashboards':
        if not setup.load_config():
            return 1
        
        grafana_config = setup.config.get('docker', {}).get('services', {}).get('grafana', {})
        setup.client = GrafanaClient(
            url='http://localhost:3000',
            username=grafana_config.get('admin_user', 'admin'),
            password=grafana_config.get('admin_password', 'admin123')
        )
        
        success = setup.create_dashboards()
        return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
