#!/bin/bash

# InfluxDB Initialization Script for Docker
# This script runs when the InfluxDB container starts
# It creates the default databases and retention policies

set -e

INFLUX_HOST="${INFLUXDB_HOST:-localhost}"
INFLUX_PORT="${INFLUXDB_PORT:-8086}"

echo "Waiting for InfluxDB to be ready..."
for i in {1..30}; do
    if influx ping -host "$INFLUX_HOST" -port "$INFLUX_PORT" > /dev/null 2>&1; then
        echo "InfluxDB is ready!"
        break
    fi
    echo "Attempt $i: InfluxDB not ready yet, waiting..."
    sleep 1
done

echo "Creating databases..."

# Create databases for different data types
DATABASES=("tick" "ohlc" "depth" "orders" "sentiment" "_internal")

for db in "${DATABASES[@]}"; do
    echo "Creating database: $db"
    influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
        -execute "CREATE DATABASE IF NOT EXISTS $db" || true
done

echo "Creating retention policies..."

# Tick data - 30 days
echo "Creating retention policy for tick data (30 days)"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
    -execute "CREATE RETENTION POLICY \"tick_30day\" ON \"tick\" DURATION 30d REPLICATION 1 DEFAULT" 2>/dev/null || \
    echo "Note: tick_30day policy may already exist"

# OHLC data - 1 year
echo "Creating retention policy for OHLC data (1 year)"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
    -execute "CREATE RETENTION POLICY \"ohlc_1year\" ON \"ohlc\" DURATION 365d REPLICATION 1 DEFAULT" 2>/dev/null || \
    echo "Note: ohlc_1year policy may already exist"

# Depth data - 7 days
echo "Creating retention policy for depth data (7 days)"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
    -execute "CREATE RETENTION POLICY \"depth_7day\" ON \"depth\" DURATION 7d REPLICATION 1 DEFAULT" 2>/dev/null || \
    echo "Note: depth_7day policy may already exist"

# Orders data - 90 days
echo "Creating retention policy for orders data (90 days)"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
    -execute "CREATE RETENTION POLICY \"orders_90day\" ON \"orders\" DURATION 90d REPLICATION 1 DEFAULT" 2>/dev/null || \
    echo "Note: orders_90day policy may already exist"

# Sentiment data - 30 days
echo "Creating retention policy for sentiment data (30 days)"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
    -execute "CREATE RETENTION POLICY \"sentiment_30day\" ON \"sentiment\" DURATION 30d REPLICATION 1 DEFAULT" 2>/dev/null || \
    echo "Note: sentiment_30day policy may already exist"

echo "Creating continuous queries..."

# Continuous query for downsampling tick to OHLC (1-hour candles)
echo "Creating continuous query for OHLC downsampling"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" \
    -database "tick" \
    -execute "
    CREATE CONTINUOUS QUERY cq_tick_ohlc ON tick 
    BEGIN 
        SELECT 
            FIRST(bid) AS open, 
            MAX(bid) AS high, 
            MIN(bid) AS low, 
            LAST(bid) AS close,
            MEAN(bid) AS mid
        INTO ohlc 
        FROM tick 
        GROUP BY time(1h), * 
    END
    " 2>/dev/null || echo "Note: Continuous query may already exist"

echo "InfluxDB initialization completed successfully!"
echo ""
echo "Available databases:"
influx -host "$INFLUX_HOST" -port "$INFLUX_PORT" -execute "SHOW DATABASES" || true

echo ""
echo "To connect:"
echo "  - HTTP API: http://$INFLUX_HOST:$INFLUX_PORT"
echo "  - CLI: influx -host $INFLUX_HOST -port $INFLUX_PORT"
