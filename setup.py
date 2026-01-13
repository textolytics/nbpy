#!/usr/bin/env python3
"""
Setup configuration for nbpy package

nbpy - ZMQ to InfluxDB pipeline for market data
A comprehensive solution for capturing market data via ZMQ and storing it in InfluxDB
with Grafana visualization support.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="nbpy",
    version="1.0.0",
    description="nbpy - ZMQ to InfluxDB pipeline for market data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="textolytics",
    author_email="",
    url="https://github.com/textolytics/nbpy",
    
    # Include db package explicitly
    packages=['db', 'db.services'],
    
    # Ensure package data is included
    include_package_data=True,
    
    python_requires=">=3.7",
    
    install_requires=[
        # InfluxDB client
        "influxdb>=5.3.0",
        # ZMQ messaging
        "pyzmq>=22.0.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
        "docker": [
            "docker>=5.0",
            "docker-compose>=1.29",
        ],
        "all": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "docker>=5.0",
            "docker-compose>=1.29",
        ],
    },
    
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    
    keywords="influxdb zmq timeseries database market data financial",
    
    project_urls={
        "Bug Reports": "https://github.com/textolytics/nbpy/issues",
        "Source": "https://github.com/textolytics/nbpy",
        "Documentation": "https://github.com/textolytics/nbpy/docs",
    },
)
