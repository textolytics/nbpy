#!/bin/bash
# InfluxDB initialization script
# Creates databases and users for nbpy ZMQ services

set -e

INFLUX_CLI="influx -host localhost -username admin -password admin123"

# Create databases
echo "Creating databases..."
$INFLUX_CLI -execute "CREATE DATABASE tick"
$INFLUX_CLI -execute "CREATE DATABASE kraken"
$INFLUX_CLI -execute "CREATE DATABASE oanda"
$INFLUX_CLI -execute "CREATE DATABASE twitter"
$INFLUX_CLI -execute "CREATE DATABASE analytics"

# Create retention policies
echo "Creating retention policies..."
$INFLUX_CLI -database tick -execute "CREATE RETENTION POLICY tick_30d ON tick DURATION 30d REPLICATION 1 DEFAULT"
$INFLUX_CLI -database kraken -execute "CREATE RETENTION POLICY kraken_30d ON kraken DURATION 30d REPLICATION 1 DEFAULT"
$INFLUX_CLI -database oanda -execute "CREATE RETENTION POLICY oanda_30d ON oanda DURATION 30d REPLICATION 1 DEFAULT"

# Create continuous queries for downsampling
echo "Creating continuous queries..."
$INFLUX_CLI -database tick -execute "CREATE CONTINUOUS QUERY cq_tick_5m ON tick BEGIN SELECT mean(bid), mean(ask), mean(last) INTO tick_5m FROM kraken_tick GROUP BY time(5m), * END"

echo "InfluxDB initialization complete!"
