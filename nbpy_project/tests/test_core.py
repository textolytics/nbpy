"""Basic tests for nbpy_zmq package."""

import pytest
from nbpy_zmq.utils import ZMQConfig, MessageBus


def test_zmq_config_defaults():
    """Test ZMQConfig uses correct defaults."""
    config = ZMQConfig()
    
    assert config.host == "localhost"
    assert config.pub_port == 5559
    assert config.sub_port == 5560
    assert config.influxdb_host == "192.168.0.33"
    assert config.influxdb_db == "tick"


def test_zmq_config_url_generation():
    """Test ZMQConfig URL generation."""
    config = ZMQConfig()
    
    url = config.get_zmq_url()
    assert url == "tcp://localhost:5559"
    
    url = config.get_zmq_url(port=9999, host="example.com")
    assert url == "tcp://example.com:9999"
    
    influx_url = config.get_influxdb_url()
    assert influx_url == "http://192.168.0.33:8086"


def test_message_bus_initialization():
    """Test MessageBus initialization."""
    config = ZMQConfig()
    bus = MessageBus(config)
    
    assert bus.config == config
    assert bus._pub_socket is None
    assert bus._sub_socket is None
    
    bus.close()


def test_message_bus_custom_config():
    """Test MessageBus with custom config."""
    custom_config = ZMQConfig(host="192.168.0.100", pub_port=9999)
    bus = MessageBus(custom_config)
    
    assert bus.config.host == "192.168.0.100"
    assert bus.config.pub_port == 9999
    
    bus.close()


def test_message_format_parse():
    """Test message format with tab separators."""
    data = "EUR_USD\x011.0820\x011.0825\x01USD_JPY\x01150.50\x01150.55\x010.0045"
    parts = data.split('\x01')
    
    assert len(parts) == 7
    assert parts[0] == "EUR_USD"
    assert parts[1] == "1.0820"
    assert parts[6] == "0.0045"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
