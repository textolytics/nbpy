"""
Configuration management for InfluxDB services in nbpy project.

Supports:
- Environment variable configuration
- Configuration file loading (.env, YAML, JSON)
- Multi-database setup
- Per-service configuration
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InfluxDBEnvironmentConfig:
    """Load InfluxDB configuration from environment variables"""
    
    # Default configuration key mappings
    ENV_MAPPING = {
        'INFLUXDB_HOST': 'host',
        'INFLUXDB_PORT': 'port',
        'INFLUXDB_USER': 'username',
        'INFLUXDB_PASSWORD': 'password',
        'INFLUXDB_DB': 'database',
        'INFLUXDB_SSL': 'ssl',
        'INFLUXDB_VERIFY_SSL': 'verify_ssl',
        'INFLUXDB_TIMEOUT': 'timeout',
        'INFLUXDB_BATCH_SIZE': 'batch_size',
        'INFLUXDB_CONSISTENCY': 'write_consistency',
        'INFLUXDB_RETENTION': 'retention_policy',
    }
    
    # Type conversions
    TYPE_CONVERTERS = {
        'port': int,
        'timeout': int,
        'batch_size': int,
        'ssl': lambda x: x.lower() == 'true',
        'verify_ssl': lambda x: x.lower() == 'true',
    }
    
    @staticmethod
    def load() -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dictionary with configuration values
        """
        config = {}
        
        for env_var, config_key in InfluxDBEnvironmentConfig.ENV_MAPPING.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Apply type conversion if needed
                if config_key in InfluxDBEnvironmentConfig.TYPE_CONVERTERS:
                    converter = InfluxDBEnvironmentConfig.TYPE_CONVERTERS[config_key]
                    value = converter(value)
                
                config[config_key] = value
        
        return config


class InfluxDBConfigFile:
    """Load InfluxDB configuration from files"""
    
    @staticmethod
    def load_json(filepath: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to JSON config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON config from {filepath}: {e}")
            return {}
    
    @staticmethod
    def load_env_file(filepath: str) -> Dict[str, Any]:
        """
        Load configuration from .env file.
        
        Args:
            filepath: Path to .env file
            
        Returns:
            Configuration dictionary
        """
        config = {}
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # Apply environment variable mappings
                        for env_var, config_key in InfluxDBEnvironmentConfig.ENV_MAPPING.items():
                            if key == env_var:
                                # Apply type conversion
                                if config_key in InfluxDBEnvironmentConfig.TYPE_CONVERTERS:
                                    converter = InfluxDBEnvironmentConfig.TYPE_CONVERTERS[config_key]
                                    value = converter(value)
                                
                                config[config_key] = value
                                break
            
            return config
        except Exception as e:
            logger.error(f"Error loading .env file from {filepath}: {e}")
            return {}
    
    @staticmethod
    def load_yaml(filepath: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            filepath: Path to YAML config file
            
        Returns:
            Configuration dictionary
        """
        try:
            import yaml
            with open(filepath, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('influxdb', {}) if config else {}
        except ImportError:
            logger.warning("PyYAML not installed, cannot load YAML config")
            return {}
        except Exception as e:
            logger.error(f"Error loading YAML config from {filepath}: {e}")
            return {}


class ServiceConfigBuilder:
    """Build configuration for specific services"""
    
    # Service-specific configurations
    SERVICE_CONFIGS = {
        'tick': {
            'database': 'tick',
            'retention_policy': 'autogen',
            'batch_size': 500,
        },
        'ohlc': {
            'database': 'ohlc',
            'retention_policy': 'autogen',
            'batch_size': 100,
        },
        'depth': {
            'database': 'depth',
            'retention_policy': 'autogen',
            'batch_size': 250,
        },
        'sentiment': {
            'database': 'sentiment',
            'retention_policy': 'autogen',
            'batch_size': 100,
        },
        'orders': {
            'database': 'orders',
            'retention_policy': 'autogen',
            'batch_size': 200,
        },
    }
    
    @staticmethod
    def build(service_name: str, base_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build configuration for a specific service.
        
        Args:
            service_name: Name of the service (e.g., 'tick', 'depth')
            base_config: Base configuration to override
            
        Returns:
            Configuration dictionary
        """
        # Start with service defaults
        config = ServiceConfigBuilder.SERVICE_CONFIGS.get(service_name, {}).copy()
        
        # Merge with base config if provided
        if base_config:
            config.update(base_config)
        
        return config


class ConfigManager:
    """Central configuration manager for nbpy database services"""
    
    def __init__(self):
        """Initialize configuration manager"""
        self.base_config: Dict[str, Any] = {}
        self.service_configs: Dict[str, Dict[str, Any]] = {}
        self._load_all()
    
    def _load_all(self):
        """Load all available configurations"""
        # Load from environment first (highest priority)
        self.base_config = InfluxDBEnvironmentConfig.load()
        
        # Try to load from config files
        config_paths = [
            Path('/home/textolytics/nbpy/db/config.json'),
            Path('/home/textolytics/nbpy/db/.env'),
            Path('/home/textolytics/nbpy/.env'),
            Path('.env'),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                if config_path.suffix == '.json':
                    file_config = InfluxDBConfigFile.load_json(str(config_path))
                elif config_path.suffix == '.env' or config_path.name == '.env':
                    file_config = InfluxDBConfigFile.load_env_file(str(config_path))
                else:
                    file_config = InfluxDBConfigFile.load_yaml(str(config_path))
                
                # Merge with existing config (file config has lower priority than env vars)
                for key, value in file_config.items():
                    if key not in self.base_config:
                        self.base_config[key] = value
                
                logger.info(f"Loaded config from {config_path}")
    
    def get_base_config(self) -> Dict[str, Any]:
        """Get base configuration"""
        return self.base_config.copy()
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific service.
        
        Args:
            service_name: Service name
            
        Returns:
            Service configuration
        """
        if service_name not in self.service_configs:
            self.service_configs[service_name] = ServiceConfigBuilder.build(
                service_name,
                self.base_config
            )
        
        return self.service_configs[service_name].copy()
    
    def register_service_config(self, service_name: str, config: Dict[str, Any]):
        """
        Register a custom service configuration.
        
        Args:
            service_name: Service name
            config: Configuration dictionary
        """
        self.service_configs[service_name] = config
        logger.info(f"Registered config for service: {service_name}")
    
    def print_config(self):
        """Print current configuration (excluding passwords)"""
        safe_config = self.base_config.copy()
        
        # Remove sensitive information
        if 'password' in safe_config:
            safe_config['password'] = '***'
        
        logger.info(f"Configuration: {json.dumps(safe_config, indent=2)}")


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create global configuration manager"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager()
    
    return _config_manager


# Example configuration file templates
EXAMPLE_CONFIG_JSON = """
{
    "host": "192.168.0.33",
    "port": 8086,
    "username": "zmq",
    "password": "zmq",
    "database": "tick",
    "ssl": false,
    "verify_ssl": true,
    "timeout": 10,
    "batch_size": 500,
    "write_consistency": "one",
    "retention_policy": "autogen"
}
"""

EXAMPLE_CONFIG_ENV = """
# InfluxDB Configuration
INFLUXDB_HOST=192.168.0.33
INFLUXDB_PORT=8086
INFLUXDB_USER=zmq
INFLUXDB_PASSWORD=zmq
INFLUXDB_DB=tick
INFLUXDB_SSL=false
INFLUXDB_VERIFY_SSL=true
INFLUXDB_TIMEOUT=10
INFLUXDB_BATCH_SIZE=500
INFLUXDB_CONSISTENCY=one
INFLUXDB_RETENTION=autogen
"""


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    manager = get_config_manager()
    manager.print_config()
    
    # Get service-specific config
    tick_config = manager.get_service_config('tick')
    logger.info(f"Tick service config: {tick_config}")
    
    # Create example config files
    config_dir = Path('/home/textolytics/nbpy/db')
    
    example_json = config_dir / 'config.example.json'
    if not example_json.exists():
        example_json.write_text(EXAMPLE_CONFIG_JSON)
        logger.info(f"Created example config: {example_json}")
    
    example_env = config_dir / '.env.example'
    if not example_env.exists():
        example_env.write_text(EXAMPLE_CONFIG_ENV)
        logger.info(f"Created example config: {example_env}")
