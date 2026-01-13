#!/usr/bin/env python3
"""
Setup Verification and Integration Test

Verifies that the nbpy ZMQ module is properly installed and all
components are working correctly.
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_command(cmd, description):
    """Run a command and report result"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing: {description}")
    logger.info(f"{'='*60}")
    logger.info(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info(f"✓ {description} - PASSED")
            if result.stdout:
                logger.info("Output:\n" + result.stdout[:500])
            return True
        else:
            logger.error(f"✗ {description} - FAILED")
            if result.stderr:
                logger.error("Error:\n" + result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"✗ {description} - TIMEOUT")
        return False
    except Exception as e:
        logger.error(f"✗ {description} - ERROR: {e}")
        return False


def main():
    """Run all setup verification tests"""
    logger.info("="*60)
    logger.info("NBPY ZMQ SETUP VERIFICATION")
    logger.info("="*60)
    
    tests = [
        (
            ["python3", "-c", "import nbpy; print('nbpy imported')"],
            "Import nbpy module"
        ),
        (
            ["python3", "-c", "from nbpy.zmq import PortConfig; print('zmq module loaded')"],
            "Import nbpy.zmq module"
        ),
        (
            ["python3", "-c", "from nbpy.zmq import validate_port_uniqueness; print(validate_port_uniqueness())"],
            "Validate port uniqueness"
        ),
        (
            ["python3", "-c", "import msgpack; print(f'msgpack version: {msgpack.version[0]}')"],
            "MessagePack library"
        ),
        (
            ["python3", "-c", "from nbpy.zmq.publishers.kraken_tick import KrakenTickPublisher; print('Publishers loaded')"],
            "Load publisher implementations"
        ),
        (
            ["python3", "-c", "from nbpy.zmq.subscribers.influxdb_tick import KrakenTickToInfluxDBSubscriber; print('Subscribers loaded')"],
            "Load subscriber implementations"
        ),
        (
            ["python3", "-m", "nbpy.zmq.validate"],
            "Run validation tests"
        ),
        (
            ["which", "nbpy-pub-kraken-tick"],
            "Check CLI entry point - publisher"
        ),
        (
            ["which", "nbpy-sub-kraken-influxdb-tick"],
            "Check CLI entry point - subscriber"
        ),
    ]
    
    results = []
    for cmd, desc in tests:
        results.append((desc, run_command(cmd, desc)))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for desc, result in results:
        status = "✓" if result else "✗"
        logger.info(f"{status} {desc}")
    
    logger.info("-"*60)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("="*60)
    
    if passed == total:
        logger.info("\n✓ All setup verification tests PASSED!")
        logger.info("\nYou can now run:")
        logger.info("  nbpy-pub-kraken-tick")
        logger.info("  nbpy-sub-kraken-influxdb-tick")
        logger.info("\nOr import and use in your code:")
        logger.info("  from nbpy.zmq.publishers.kraken_tick import KrakenTickPublisher")
        logger.info("  from nbpy.zmq.subscribers.influxdb_tick import KrakenTickToInfluxDBSubscriber")
        return 0
    else:
        logger.error("\n✗ Some tests failed. Please check the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
