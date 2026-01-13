#!/bin/bash

################################################################################
# nbpy_zmq_service.sh - Aggregated ZMQ Publisher/Subscriber Service Manager
# 
# This script manages multiple ZMQ-based services for the nbpy project:
# - Publishers: oanda, kraken data streams
# - Subscribers: influxdb, kapacitor, grakn databases
# - Forwarder: message distribution device
#
# Usage: nbpy_zmq_service.sh {start|stop|status|restart|install|uninstall} [service_name]
################################################################################

set -e

# Configuration
SERVICE_HOME="/home/textolytics/nbpy/python/scripts/zmq"
PYTHON_BIN="/home/textolytics/nbpy/bin/python"
SERVICES_DIR="/etc/init.d"
LOG_DIR="/var/log/nbpy_zmq"
RUN_DIR="/var/run/nbpy_zmq"
DEFAULT_USER="textolytics"

# Service definitions: name:description:command
declare -a SERVICES=(
  "nbpy_zmq_forwarder_server:ZMQ Forwarder Server:${PYTHON_BIN} ${SERVICE_HOME}/forwarder_server.py"
  "nbpy_zmq_pub_oanda_tick:OANDA Tick Data Publisher:${PYTHON_BIN} ${SERVICE_HOME}/pub_oanda_tick.py"
  "nbpy_zmq_pub_kraken_tick:Kraken Tick Data Publisher:${PYTHON_BIN} ${SERVICE_HOME}/pub_kraken_tick.py"
  "nbpy_zmq_pub_kraken_depth:Kraken Depth Data Publisher:${PYTHON_BIN} ${SERVICE_HOME}/pub_kraken_EURUSD_depth.py"
  "nbpy_zmq_sub_oanda_influxdb:OANDA to InfluxDB Subscriber:${PYTHON_BIN} ${SERVICE_HOME}/sub_oanda_influxdb.py"
  "nbpy_zmq_sub_kraken_influxdb:Kraken to InfluxDB Subscriber:${PYTHON_BIN} ${SERVICE_HOME}/sub_kraken_influxdb.py"
  "nbpy_zmq_sub_kraken_depth_influxdb:Kraken Depth to InfluxDB Subscriber:${PYTHON_BIN} ${SERVICE_HOME}/sub_kraken_influxdb_depth.py"
)

# Create necessary directories
init_directories() {
  mkdir -p "$LOG_DIR"
  mkdir -p "$RUN_DIR"
  chmod 755 "$LOG_DIR"
  chmod 755 "$RUN_DIR"
}

# Function to generate service file
generate_service_file() {
  local service_name="$1"
  local service_desc="$2"
  local service_cmd="$3"
  local service_file="${SERVICES_DIR}/${service_name}"
  
  cat > "$service_file" << 'EOFSERVICE'
#!/bin/sh
### BEGIN INIT INFO
# Provides:          <SERVICE_NAME>
# Required-Start:    $local_fs $network $named $time $syslog
# Required-Stop:     $local_fs $network $named $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       <SERVICE_DESC>
### END INIT INFO

SCRIPT="<SERVICE_CMD>"
RUNAS=<SERVICE_USER>
SERVICE_NAME="<SERVICE_NAME>"
LOG_DIR="/var/log/nbpy_zmq"
RUN_DIR="/var/run/nbpy_zmq"

PIDFILE="${RUN_DIR}/${SERVICE_NAME}.pid"
LOGFILE="${LOG_DIR}/${SERVICE_NAME}.log"

start() {
  if [ -f "$PIDFILE" ] && [ -s "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
    echo "Service $SERVICE_NAME already running (PID: $(cat $PIDFILE))" >&2
    return 1
  fi
  
  echo "Starting service $SERVICE_NAME…" >&2
  
  # Ensure directories exist
  mkdir -p "$LOG_DIR" "$RUN_DIR"
  
  # Start the service
  local CMD="$SCRIPT &> \"$LOGFILE\" & echo \$!"
  su -c "$CMD" "$RUNAS" > "$PIDFILE"
  
  sleep 2
  
  if [ -f "$PIDFILE" ] && [ -s "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "$SERVICE_NAME started successfully (PID: $PID)" >&2
      return 0
    else
      echo "Failed to start $SERVICE_NAME" >&2
      rm -f "$PIDFILE"
      return 1
    fi
  else
    echo "Failed to start $SERVICE_NAME - no PID file" >&2
    return 1
  fi
}

stop() {
  if [ ! -f "$PIDFILE" ] || ! kill -0 $(cat "$PIDFILE") 2>/dev/null; then
    echo "Service $SERVICE_NAME not running" >&2
    return 1
  fi
  
  echo "Stopping service $SERVICE_NAME…" >&2
  PID=$(cat "$PIDFILE")
  
  # Try graceful kill first
  kill -15 "$PID" 2>/dev/null || true
  sleep 2
  
  # Force kill if still running
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" 2>/dev/null || true
    sleep 1
  fi
  
  rm -f "$PIDFILE"
  echo "Service $SERVICE_NAME stopped" >&2
}

status() {
  printf "%-50s" "Checking $SERVICE_NAME..."
  if [ -f "$PIDFILE" ] && [ -s "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "Running (PID: $PID)" >&2
      return 0
    else
      echo "Process dead but pidfile exists" >&2
      return 1
    fi
  else
    echo "Not running" >&2
    return 1
  fi
}

restart() {
  echo "Restarting service $SERVICE_NAME..." >&2
  stop || true
  sleep 1
  start
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status
    ;;
  restart)
    restart
    ;;
  *)
    echo "Usage: $0 {start|stop|status|restart}"
    exit 1
    ;;
esac

exit $?
EOFSERVICE

  # Replace placeholders
  sed -i "s|<SERVICE_NAME>|$service_name|g" "$service_file"
  sed -i "s|<SERVICE_DESC>|$service_desc|g" "$service_file"
  sed -i "s|<SERVICE_CMD>|$service_cmd|g" "$service_file"
  sed -i "s|<SERVICE_USER>|$DEFAULT_USER|g" "$service_file"
  
  chmod 755 "$service_file"
}

# Function to install all services
install_all() {
  echo "=== Installing nbpy ZMQ Services ==="
  init_directories
  
  # Ensure log directory is owned by the service user
  chown -R "$DEFAULT_USER:$DEFAULT_USER" "$LOG_DIR" "$RUN_DIR" 2>/dev/null || sudo chown -R "$DEFAULT_USER:$DEFAULT_USER" "$LOG_DIR" "$RUN_DIR"
  
  for service in "${SERVICES[@]}"; do
    IFS=':' read -r name desc cmd <<< "$service"
    echo "Installing $name..."
    
    if [ ! -w "$SERVICES_DIR" ]; then
      echo "✗ No write permission to $SERVICES_DIR. Please run with sudo."
      return 1
    fi
    
    generate_service_file "$name" "$desc" "$cmd"
    update-rc.d "$name" defaults 2>/dev/null || sudo update-rc.d "$name" defaults
    echo "✓ Installed $name"
  done
  
  echo "=== Installation Complete ==="
  echo "Start all services with: $0 start all"
}

# Function to uninstall all services
uninstall_all() {
  echo "=== Uninstalling nbpy ZMQ Services ==="
  
  read -p "Are you sure you want to uninstall all ZMQ services? [yes/No] " -n 3 -r
  echo
  
  if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Abort!"
    return 1
  fi
  
  for service in "${SERVICES[@]}"; do
    IFS=':' read -r name _ _ <<< "$service"
    echo "Uninstalling $name..."
    
    if [ -f "${SERVICES_DIR}/${name}" ]; then
      service "$name" stop 2>/dev/null || true
      update-rc.d -f "$name" remove 2>/dev/null || sudo update-rc.d -f "$name" remove
      rm -f "${SERVICES_DIR}/${name}"
      rm -f "${RUN_DIR}/${name}.pid"
      echo "✓ Uninstalled $name"
    fi
  done
  
  echo "=== Uninstallation Complete ==="
}

# Function to manage all services
manage_all_services() {
  local action="$1"
  
  case "$action" in
    start)
      echo "=== Starting all nbpy ZMQ services ==="
      for service in "${SERVICES[@]}"; do
        IFS=':' read -r name _ _ <<< "$service"
        echo "Starting $name..."
        if [ -f "${SERVICES_DIR}/${name}" ]; then
          service "$name" start || true
        fi
      done
      ;;
    stop)
      echo "=== Stopping all nbpy ZMQ services ==="
      for service in "${SERVICES[@]}"; do
        IFS=':' read -r name _ _ <<< "$service"
        echo "Stopping $name..."
        if [ -f "${SERVICES_DIR}/${name}" ]; then
          service "$name" stop || true
        fi
      done
      ;;
    status)
      echo "=== Status of all nbpy ZMQ services ==="
      for service in "${SERVICES[@]}"; do
        IFS=':' read -r name _ _ <<< "$service"
        printf "%-40s " "$name:"
        if [ -f "${SERVICES_DIR}/${name}" ]; then
          service "$name" status || true
        else
          echo "Not installed"
        fi
      done
      ;;
    restart)
      manage_all_services stop
      sleep 2
      manage_all_services start
      ;;
    *)
      echo "Usage: $0 {start|stop|status|restart} all"
      return 1
      ;;
  esac
}

# Main script logic
main() {
  local action="${1:-status}"
  local target="${2:-all}"
  
  case "$action" in
    install)
      install_all
      ;;
    uninstall)
      uninstall_all
      ;;
    start|stop|status|restart)
      if [ "$target" = "all" ]; then
        manage_all_services "$action"
      else
        # Manage individual service
        if [ ! -f "${SERVICES_DIR}/${target}" ]; then
          echo "Service $target not found or not installed"
          return 1
        fi
        service "$target" "$action"
      fi
      ;;
    list)
      echo "=== Available nbpy ZMQ Services ==="
      for service in "${SERVICES[@]}"; do
        IFS=':' read -r name desc _ <<< "$service"
        printf "%-40s %s\n" "$name:" "$desc"
      done
      ;;
    help)
      cat << 'EOFHELP'
nbpy_zmq_service.sh - Aggregated ZMQ Publisher/Subscriber Service Manager

Usage: nbpy_zmq_service.sh {action} [target]

Actions:
  install          Install all ZMQ services (requires sudo)
  uninstall        Uninstall all ZMQ services (requires sudo)
  start [all|name] Start all services or a specific service
  stop [all|name]  Stop all services or a specific service
  status [all|name] Show status of all services or a specific service
  restart [all|name] Restart all services or a specific service
  list             List all available services
  help             Show this help message

Examples:
  nbpy_zmq_service.sh install
  nbpy_zmq_service.sh start all
  nbpy_zmq_service.sh status nbpy_zmq_pub_oanda_tick
  nbpy_zmq_service.sh stop nbpy_zmq_sub_oanda_influxdb

Log Files:
  /var/log/nbpy_zmq/[service_name].log

PID Files:
  /var/run/nbpy_zmq/[service_name].pid

EOFHELP
      ;;
    *)
      echo "Unknown action: $action"
      echo "Use '$0 help' for usage information"
      return 1
      ;;
  esac
}

# Run main function
main "$@"
exit $?
