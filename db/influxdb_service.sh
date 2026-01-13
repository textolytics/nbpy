#!/bin/bash

################################################################################
# influxdb_service.sh - InfluxDB Server Management Script
#
# Manages InfluxDB service for nbpy project on localhost:8086
# Supports: start, stop, status, restart, install, logs, config
#
# Usage: influxdb_service.sh {action} [options]
################################################################################

set -e

# Configuration
INFLUXDB_HOME="${INFLUXDB_HOME:-/opt/influxdb}"
INFLUXDB_DATA_DIR="${INFLUXDB_DATA_DIR:-/var/lib/influxdb}"
INFLUXDB_CONFIG="${INFLUXDB_CONFIG:-/etc/influxdb/influxdb.conf}"
INFLUXDB_LOG_DIR="${INFLUXDB_LOG_DIR:-/var/log/influxdb}"
INFLUXDB_PID_FILE="${INFLUXDB_PID_FILE:-/var/run/influxdb/influxdb.pid}"
INFLUXDB_HOST="${INFLUXDB_HOST:-localhost}"
INFLUXDB_PORT="${INFLUXDB_PORT:-8086}"
INFLUXDB_USER="${INFLUXDB_USER:-influxdb}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if InfluxDB is installed
check_installation() {
    if [ ! -d "$INFLUXDB_HOME" ]; then
        error "InfluxDB not found at $INFLUXDB_HOME"
        return 1
    fi
    
    if [ ! -f "$INFLUXDB_HOME/usr/bin/influxd" ]; then
        error "InfluxDB binary not found at $INFLUXDB_HOME/usr/bin/influxd"
        return 1
    fi
    
    return 0
}

# Check if InfluxDB is running
is_running() {
    if [ ! -f "$INFLUXDB_PID_FILE" ]; then
        return 1
    fi
    
    local pid=$(cat "$INFLUXDB_PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    
    return 1
}

# Initialize directories and permissions
init_directories() {
    log "Initializing InfluxDB directories..."
    
    # Create required directories
    mkdir -p "$INFLUXDB_DATA_DIR"
    mkdir -p "$INFLUXDB_LOG_DIR"
    mkdir -p "$(dirname "$INFLUXDB_PID_FILE")"
    mkdir -p "$(dirname "$INFLUXDB_CONFIG")"
    
    # Set proper permissions
    if command -v chown &> /dev/null; then
        chown -R "$INFLUXDB_USER:$INFLUXDB_USER" "$INFLUXDB_DATA_DIR" 2>/dev/null || sudo chown -R "$INFLUXDB_USER:$INFLUXDB_USER" "$INFLUXDB_DATA_DIR"
        chown -R "$INFLUXDB_USER:$INFLUXDB_USER" "$INFLUXDB_LOG_DIR" 2>/dev/null || sudo chown -R "$INFLUXDB_USER:$INFLUXDB_USER" "$INFLUXDB_LOG_DIR"
    fi
    
    chmod 755 "$INFLUXDB_DATA_DIR" "$INFLUXDB_LOG_DIR"
    
    success "Directories initialized"
}

# Generate default configuration
generate_config() {
    log "Generating InfluxDB configuration..."
    
    if [ -f "$INFLUXDB_CONFIG" ]; then
        warning "Configuration already exists at $INFLUXDB_CONFIG"
        return 0
    fi
    
    # Create config directory
    mkdir -p "$(dirname "$INFLUXDB_CONFIG")"
    
    cat > "$INFLUXDB_CONFIG" << 'EOF'
# InfluxDB Configuration for nbpy Project
# Generated: $(date)

[meta]
  dir = "/var/lib/influxdb/meta"
  retention-autocreate = true
  logging-enabled = true

[data]
  dir = "/var/lib/influxdb/data"
  index-version = "inmem"
  wal-dir = "/var/lib/influxdb/wal"
  wal-fsync-delay = "0s"
  validate-keys = false
  cache-max-memory-bytes = 1073741824
  cache-snapshot-memory-bytes = 26214400
  cache-snapshot-write-cold-duration = "10m0s"
  compact-full-write-cold-duration = "4h0m0s"
  max-concurrent-compactions = 0
  compact-throughput = 52428800
  compact-throughput-burst = 52428800
  max-series-per-database = 1000000
  max-values-per-tag = 100000

[coordinator]
  write-timeout = "10s"
  max-concurrent-queries = 0
  query-timeout = "0s"
  log-queries-after = "0s"
  max-select-point = 0
  max-select-series = 0
  max-select-buckets = 0

[retention]
  enabled = true
  check-interval = "30m0s"

[shard-precreation]
  enabled = true
  check-interval = "10m0s"
  advance-period = "30m0s"

[monitor]
  store-enabled = true
  store-database = "_internal"
  store-interval = "10s"

[subscriber]
  enabled = true
  http-timeout = "30s"
  insecure-skip-verify = false
  ca-certs = ""
  write-concurrency = 40
  write-buffer-size = 1000

[[udp]]
  enabled = false
  bind-address = ":8089"
  database = "udp"
  retention-policy = ""
  batch-size = 5000
  batch-pending = 10
  batch-timeout = "1s"
  read-buffer = 0

[http]
  enabled = true
  bind-address = ":8086"
  auth-enabled = false
  log-enabled = true
  suppress-write-log = false
  write-tracing = false
  pprof-enabled = false
  pprof-auth-enabled = false
  debug-pprof-enabled = false
  ping-auth-enabled = false
  https-enabled = false
  https-certificate = ""
  https-private-key = ""
  shared-secret = ""
  max-row-limit = 0
  max-connection-limit = 0
  unix-socket-enabled = false
  unix-socket-permissions = ""
  bind-socket = ""
  max-header-bytes = 1048576
  access-log-path = ""
  access-log-status-filters = []
  max-body-size = 25000000
  stats-enabled = true
  stats-interval = "10s"

[logging]
  format = "auto"
  level = "info"
  suppress-logo = false

[[graphite]]
  enabled = false
  bind-address = ":2003"
  database = "graphite"
  retention-policy = ""
  protocol = "tcp"
  batch-size = 5000
  batch-pending = 10
  batch-timeout = "1s"
  consistency-level = "one"
  separator = "."
  udp-read-buffer = 0

[[collectd]]
  enabled = false
  bind-address = ":25826"
  database = "collectd"
  retention-policy = ""
  batch-size = 5000
  batch-pending = 10
  batch-timeout = "10s"
  read-buffer = 0
  typesdb = "/usr/share/collectd/types.db"
  security-level = "none"
  auth-file = ""
  parse-multivalue-tags = false

[[opentsdb]]
  enabled = false
  bind-address = ":4242"
  database = "opentsdb"
  retention-policy = ""
  consistency-level = "one"
  tls-enabled = false
  certificate = ""
  batch-size = 1000
  batch-pending = 5
  batch-timeout = "1s"

[[influxql]]
  enabled = true
  log-enabled = true
  suppress-write-log = false

[continuous_queries]
  enabled = true
  log-enabled = true
  query-stats-enabled = false
  run-interval = "1s"
EOF
    
    success "Configuration generated at $INFLUXDB_CONFIG"
}

# Install InfluxDB
install_influxdb() {
    log "Installing InfluxDB..."
    
    if command -v influxd &> /dev/null; then
        success "InfluxDB is already installed"
        influxd version
        return 0
    fi
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        log "Using apt-get to install InfluxDB..."
        curl -s https://repos.influxdata.com/influxdb.key | sudo apt-key add - 2>/dev/null || true
        echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y influxdb
        
    elif command -v yum &> /dev/null; then
        log "Using yum to install InfluxDB..."
        sudo yum install -y influxdb
        
    elif command -v brew &> /dev/null; then
        log "Using brew to install InfluxDB..."
        brew install influxdb
        
    else
        error "Could not detect package manager"
        return 1
    fi
    
    success "InfluxDB installed successfully"
}

# Start InfluxDB service
start_service() {
    log "Starting InfluxDB service..."
    
    if is_running; then
        warning "InfluxDB is already running (PID: $(cat "$INFLUXDB_PID_FILE"))"
        return 0
    fi
    
    if ! check_installation; then
        error "InfluxDB installation check failed"
        return 1
    fi
    
    # Initialize directories
    init_directories
    
    # Generate config if needed
    if [ ! -f "$INFLUXDB_CONFIG" ]; then
        generate_config
    fi
    
    # Start InfluxDB
    local influxd_bin="$INFLUXDB_HOME/usr/bin/influxd"
    
    if [ ! -f "$influxd_bin" ]; then
        influxd_bin=$(which influxd)
    fi
    
    log "Starting influxd: $influxd_bin"
    
    # Start daemon
    nohup "$influxd_bin" \
        -config "$INFLUXDB_CONFIG" \
        -pidfile "$INFLUXDB_PID_FILE" \
        >> "$INFLUXDB_LOG_DIR/influxdb.log" 2>&1 &
    
    local pid=$!
    sleep 2
    
    if is_running; then
        success "InfluxDB started successfully (PID: $pid)"
        success "Server running at http://$INFLUXDB_HOST:$INFLUXDB_PORT"
        return 0
    else
        error "Failed to start InfluxDB"
        return 1
    fi
}

# Stop InfluxDB service
stop_service() {
    log "Stopping InfluxDB service..."
    
    if ! is_running; then
        warning "InfluxDB is not running"
        return 0
    fi
    
    local pid=$(cat "$INFLUXDB_PID_FILE")
    log "Stopping process (PID: $pid)..."
    
    # Try graceful shutdown
    kill -15 "$pid" 2>/dev/null || true
    sleep 2
    
    # Force kill if still running
    if kill -0 "$pid" 2>/dev/null; then
        warning "Process still running, forcing shutdown..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    # Remove PID file
    rm -f "$INFLUXDB_PID_FILE"
    
    success "InfluxDB stopped"
}

# Restart InfluxDB service
restart_service() {
    log "Restarting InfluxDB service..."
    stop_service
    sleep 2
    start_service
}

# Check service status
status_service() {
    log "Checking InfluxDB status..."
    
    if is_running; then
        local pid=$(cat "$INFLUXDB_PID_FILE")
        success "InfluxDB is running (PID: $pid)"
        
        # Try to connect and get version
        if command -v influx &> /dev/null; then
            log "Server details:"
            influx --host "$INFLUXDB_HOST" --port "$INFLUXDB_PORT" ping 2>/dev/null || true
        fi
        
        return 0
    else
        error "InfluxDB is not running"
        return 1
    fi
}

# Show logs
show_logs() {
    if [ ! -f "$INFLUXDB_LOG_DIR/influxdb.log" ]; then
        error "Log file not found: $INFLUXDB_LOG_DIR/influxdb.log"
        return 1
    fi
    
    log "InfluxDB logs (last 50 lines):"
    tail -50 "$INFLUXDB_LOG_DIR/influxdb.log"
}

# Follow logs
follow_logs() {
    if [ ! -f "$INFLUXDB_LOG_DIR/influxdb.log" ]; then
        error "Log file not found: $INFLUXDB_LOG_DIR/influxdb.log"
        return 1
    fi
    
    log "Following InfluxDB logs (press Ctrl+C to exit)..."
    tail -f "$INFLUXDB_LOG_DIR/influxdb.log"
}

# Show configuration
show_config() {
    if [ ! -f "$INFLUXDB_CONFIG" ]; then
        error "Configuration file not found: $INFLUXDB_CONFIG"
        return 1
    fi
    
    log "InfluxDB Configuration:"
    cat "$INFLUXDB_CONFIG"
}

# Initialize database with default databases and retention policies
init_database() {
    log "Initializing InfluxDB databases..."
    
    if ! is_running; then
        error "InfluxDB is not running"
        return 1
    fi
    
    if ! command -v influx &> /dev/null; then
        warning "influx CLI not found, skipping database initialization"
        return 0
    fi
    
    # Create databases
    local databases=("tick" "ohlc" "depth" "orders" "sentiment")
    
    for db in "${databases[@]}"; do
        log "Creating database: $db"
        influx --host "$INFLUXDB_HOST" --port "$INFLUXDB_PORT" \
            -execute "CREATE DATABASE IF NOT EXISTS $db" || true
    done
    
    # Create retention policies
    log "Creating retention policies..."
    
    # 30-day retention for tick data
    influx --host "$INFLUXDB_HOST" --port "$INFLUXDB_PORT" \
        -execute "CREATE RETENTION POLICY \"tick_30day\" ON \"tick\" DURATION 30d REPLICATION 1 DEFAULT" 2>/dev/null || true
    
    # 1-year retention for OHLC
    influx --host "$INFLUXDB_HOST" --port "$INFLUXDB_PORT" \
        -execute "CREATE RETENTION POLICY \"ohlc_1year\" ON \"ohlc\" DURATION 365d REPLICATION 1 DEFAULT" 2>/dev/null || true
    
    success "Database initialization completed"
}

# Display help
show_help() {
    cat << 'EOF'
InfluxDB Service Management Script for nbpy Project

Usage: influxdb_service.sh {action} [options]

Actions:
  install              Install InfluxDB on this system
  start                Start InfluxDB service
  stop                 Stop InfluxDB service
  restart              Restart InfluxDB service
  status               Show InfluxDB service status
  init-db              Initialize databases and retention policies
  logs                 Show recent logs
  follow               Follow logs in real-time (Ctrl+C to exit)
  config               Show current configuration
  generate-config      Generate default configuration file
  help                 Show this help message

Environment Variables:
  INFLUXDB_HOME        InfluxDB installation directory (default: /opt/influxdb)
  INFLUXDB_DATA_DIR    Data directory (default: /var/lib/influxdb)
  INFLUXDB_CONFIG      Configuration file path (default: /etc/influxdb/influxdb.conf)
  INFLUXDB_LOG_DIR     Log directory (default: /var/log/influxdb)
  INFLUXDB_PID_FILE    PID file path (default: /var/run/influxdb/influxdb.pid)
  INFLUXDB_HOST        Server host (default: localhost)
  INFLUXDB_PORT        Server port (default: 8086)
  INFLUXDB_USER        System user (default: influxdb)

Examples:
  # Install InfluxDB
  influxdb_service.sh install

  # Start service
  influxdb_service.sh start

  # Check status
  influxdb_service.sh status

  # View logs
  influxdb_service.sh logs

  # Follow logs
  influxdb_service.sh follow

  # Initialize databases
  influxdb_service.sh init-db

Configuration:
  Default configuration file: /etc/influxdb/influxdb.conf
  Data directory: /var/lib/influxdb
  Log directory: /var/log/influxdb

Connection:
  HTTP API: http://localhost:8086
  CLI: influx -host localhost -port 8086

For more information: https://docs.influxdata.com

EOF
}

# Main script logic
main() {
    local action="${1:-status}"
    
    case "$action" in
        install)
            install_influxdb
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        init-db)
            init_database
            ;;
        logs)
            show_logs
            ;;
        follow)
            follow_logs
            ;;
        config)
            show_config
            ;;
        generate-config)
            generate_config
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown action: $action"
            echo "Use 'influxdb_service.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
exit $?
