#!/usr/bin/env python3
"""
InfluxDB Retention Policy Configuration

Manages creation and configuration of InfluxDB retention policies.
Handles:
- Default retention policies
- Measurement-specific policies
- Shard duration configuration
- Data cleanup and compaction
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from influxdb import InfluxDBClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/retention_policy.log')
    ]
)
logger = logging.getLogger(__name__)


class RetentionPolicyManager:
    """
    Manages InfluxDB retention policies for time-series data.
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8086,
        username: str = 'admin',
        password: str = 'admin123',
        database: str = 'tick'
    ):
        """
        Initialize retention policy manager.
        
        Args:
            host: InfluxDB host
            port: InfluxDB port
            username: Admin username
            password: Admin password
            database: Target database name
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client: Optional[InfluxDBClient] = None
        
        logger.info(f"Initialized RetentionPolicyManager for {database} on {host}:{port}")
    
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
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from InfluxDB"""
        if self.client:
            try:
                self.client.close()
                logger.info("Disconnected from InfluxDB")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def create_database_if_not_exists(self) -> bool:
        """Create database if it doesn't exist"""
        try:
            databases = [db['name'] for db in self.client.get_list_database()]
            
            if self.database in databases:
                logger.info(f"✓ Database '{self.database}' already exists")
                return True
            
            logger.info(f"Creating database '{self.database}'...")
            self.client.create_database(self.database)
            logger.info(f"✓ Database '{self.database}' created")
            return True
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def create_retention_policy(
        self,
        name: str,
        duration: str,
        replication: int = 1,
        shard_duration: Optional[str] = None,
        default: bool = False
    ) -> bool:
        """
        Create a retention policy.
        
        Args:
            name: Policy name
            duration: Data retention duration (e.g., '30d', '7d', '365d')
            replication: Replication factor
            shard_duration: Shard duration (e.g., '1d', '6h')
            default: Set as default policy
            
        Returns:
            True if successful
        """
        try:
            # Check if policy exists
            policies = self.client.get_list_retention_policies(self.database)
            existing_names = [p['name'] for p in policies]
            
            if name in existing_names:
                logger.info(f"✓ Retention policy '{name}' already exists")
                return True
            
            logger.info(f"Creating retention policy: {name} (duration: {duration})")
            
            self.client.create_retention_policy(
                name=name,
                duration=duration,
                replication=replication,
                shard_duration=shard_duration,
                database=self.database,
                default=default
            )
            
            logger.info(f"✓ Retention policy '{name}' created")
            return True
        except Exception as e:
            logger.error(f"Error creating retention policy '{name}': {e}")
            return False
    
    def set_default_retention_policy(self, name: str) -> bool:
        """Set a retention policy as default"""
        try:
            logger.info(f"Setting '{name}' as default retention policy...")
            self.client.alter_retention_policy(
                name=name,
                database=self.database,
                default=True
            )
            logger.info(f"✓ '{name}' is now default")
            return True
        except Exception as e:
            logger.error(f"Error setting default policy: {e}")
            return False
    
    def list_retention_policies(self) -> List[Dict[str, Any]]:
        """List all retention policies for the database"""
        try:
            policies = self.client.get_list_retention_policies(self.database)
            
            logger.info("Current retention policies:")
            for policy in policies:
                default_marker = " (DEFAULT)" if policy.get('default', False) else ""
                # Handle both 'replicationFactor' and 'replication' keys for compatibility
                replication_factor = policy.get('replicationFactor', policy.get('replication', 'N/A'))
                logger.info(
                    f"  - {policy['name']}: {policy['duration']} "
                    f"(replication: {replication_factor}, "
                    f"shardDuration: {policy.get('shardDuration', 'N/A')})"
                    f"{default_marker}"
                )
            
            return policies
        except Exception as e:
            logger.error(f"Error listing retention policies: {e}")
            return []
    
    def configure_from_config(self, config: Dict[str, Any]) -> bool:
        """Configure retention policies from config dictionary"""
        try:
            influx_config = config.get('influxdb', {})
            retention_policies = influx_config.get('retention_policies', {})
            
            logger.info("=" * 70)
            logger.info("CONFIGURING RETENTION POLICIES")
            logger.info("=" * 70)
            
            success = True
            default_policy = None
            
            for policy_name, policy_config in retention_policies.items():
                is_default = policy_config.get('default', False)
                
                if not self.create_retention_policy(
                    name=policy_name,
                    duration=policy_config['duration'],
                    replication=policy_config.get('replication', 1),
                    shard_duration=policy_config.get('shard_duration'),
                    default=False  # Set default later
                ):
                    success = False
                
                if is_default:
                    default_policy = policy_name
            
            # Set default policy if specified
            if default_policy:
                if not self.set_default_retention_policy(default_policy):
                    success = False
            
            # List configured policies
            self.list_retention_policies()
            
            logger.info("=" * 70)
            if success:
                logger.info("✓ RETENTION POLICIES CONFIGURED SUCCESSFULLY")
            else:
                logger.warning("⚠ SOME RETENTION POLICIES FAILED")
            logger.info("=" * 70)
            
            return success
        except Exception as e:
            logger.error(f"Error configuring retention policies: {e}")
            return False
    
    def cleanup_old_data(self, measurement: str, older_than_days: int = 30) -> bool:
        """Delete data older than specified days from a measurement"""
        try:
            logger.warning(
                f"Deleting data from '{measurement}' older than {older_than_days} days..."
            )
            
            query = f"DELETE FROM {measurement} WHERE time < now() - {older_than_days}d"
            self.client.query(query)
            
            logger.info(f"✓ Cleanup completed for '{measurement}'")
            return True
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False
    
    def get_measurements(self) -> List[str]:
        """Get all measurements in the database"""
        try:
            result = self.client.query("SHOW MEASUREMENTS")
            measurements = [item['name'] for item in result.get_points()]
            
            logger.info(f"Measurements in '{self.database}':")
            for measurement in measurements:
                logger.info(f"  - {measurement}")
            
            return measurements
        except Exception as e:
            logger.error(f"Error getting measurements: {e}")
            return []
    
    def get_data_points_count(self, measurement: str) -> int:
        """Get count of data points in a measurement"""
        try:
            query = f"SELECT COUNT(*) FROM {measurement}"
            result = self.client.query(query)
            
            for point in result.get_points():
                return point.get('count', 0)
            
            return 0
        except Exception as e:
            logger.error(f"Error getting data points count: {e}")
            return 0
    
    def show_database_stats(self) -> Dict[str, Any]:
        """Show database statistics"""
        try:
            stats = {
                'database': self.database,
                'measurements': {}
            }
            
            measurements = self.get_measurements()
            
            for measurement in measurements:
                count = self.get_data_points_count(measurement)
                stats['measurements'][measurement] = {
                    'points': count
                }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def print_stats(self):
        """Print formatted database statistics"""
        stats = self.show_database_stats()
        
        if not stats:
            logger.warning("No statistics available")
            return
        
        logger.info("=" * 70)
        logger.info("DATABASE STATISTICS")
        logger.info("=" * 70)
        logger.info(f"Database: {stats['database']}")
        logger.info("Measurements:")
        
        for measurement, info in stats['measurements'].items():
            logger.info(f"  - {measurement}: {info['points']} points")
        
        logger.info("=" * 70)


def main():
    """Entry point for retention policy manager"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='InfluxDB Retention Policy Manager'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='InfluxDB host'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8086,
        help='InfluxDB port'
    )
    parser.add_argument(
        '--database',
        default='tick',
        help='Database name'
    )
    parser.add_argument(
        '--config',
        default='integration_config.json',
        help='Configuration file'
    )
    parser.add_argument(
        'command',
        choices=['create', 'list', 'stats', 'cleanup'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    manager = RetentionPolicyManager(
        host=args.host,
        port=args.port,
        database=args.database
    )
    
    if not manager.connect():
        return 1
    
    try:
        if args.command == 'create':
            # Load config and create policies
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            success = manager.create_database_if_not_exists()
            if success:
                success = manager.configure_from_config(config)
            
            return 0 if success else 1
        
        elif args.command == 'list':
            manager.list_retention_policies()
            return 0
        
        elif args.command == 'stats':
            manager.print_stats()
            return 0
        
        elif args.command == 'cleanup':
            # Example cleanup
            measurements = manager.get_measurements()
            for measurement in measurements:
                manager.cleanup_old_data(measurement, older_than_days=30)
            return 0
    
    finally:
        manager.disconnect()


if __name__ == '__main__':
    import sys
    sys.exit(main())
