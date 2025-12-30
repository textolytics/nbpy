"""Setup configuration for nbpy_zmq package."""

from setuptools import setup, find_packages


setup(
    name="nbpy-zmq",
    version="0.1.0",
    author="nbpy developers",
    description="ZMQ-based market data ETL and analytics framework for forex and crypto",
    long_description=open("README.md", encoding="utf-8").read() if __name__ != "__main__" else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nbpy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pyzmq>=27.0.0",
        "influxdb>=5.3.1",
        "requests>=2.28.0",
        "ccs>=0.1.11",
        "vaderSentiment>=3.3.2",
        "psycopg2-binary>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
    },
)
