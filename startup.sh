#!/bin/bash
################################################################################
#                                                                              #
#                    NBPY ZMQ MICROSERVICES STARTUP SCRIPT                    #
#                                                                              #
# This script orchestrates the startup of all nbpy ZMQ services including:   #
#   - InfluxDB container (time-series database)                               #
#   - Grafana container (visualization and dashboards)                        #
#   - Python ZMQ publishers (data sources)                                    #
#   - Python ZMQ subscribers (data sinks to InfluxDB/PostgreSQL/etc)          #
#                                                                              #
# Usage: ./startup.sh [command]                                               #
#   - start     : Start all services                                          #
#   - stop      : Stop all services                                           #
#   - restart   : Restart all services                                        #
#   - logs      : Show service logs                                           #
#   - status    : Show service status                                         #
#   - config    : Show configuration                                          #
#                                                                              #
################################################################################

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="${SCRIPT_DIR}/nbpy/bin/python"
VENV_PIP="${SCRIPT_DIR}/nbpy/bin/pip"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_DIR="${SCRIPT_DIR}/.pids"
DOCKER_COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration constants
INFLUXDB_HOST="localhost"
INFLUXDB_PORT="8086"
GRAFANA_PORT="3000"
ZMQ_PUBLISHERS=(
    "kraken-tick"
    "kraken-depth"
    "kraken-orders"
    "oanda-tick"
    "betfair-stream"
)
ZMQ_SUBSCRIBERS=(
    "kraken-influxdb-tick"
    "kraken-influxdb-depth"
    "oanda-influxdb-tick"
    "kraken-pgsql-tick"
)

################################################################################
# Utility Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}${1}${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Create necessary directories
setup_directories() {
    mkdir -p "${LOG_DIR}"
    mkdir -p "${PID_DIR}"
    chmod 755 "${LOG_DIR}" "${PID_DIR}"
}

# Verify Python environment
verify_venv() {
    if [ ! -f "${VENV_PYTHON}" ]; then
        log_error "Python virtual environment not found at ${VENV_PYTHON}"
        log_info "Create venv with: python -m venv ${SCRIPT_DIR}/nbpy"
        exit 1
    fi
    
    log_success "Python environment verified: ${VENV_PYTHON}"
}

# Verify nbpy module is installed
verify_nbpy_installation() {
    log_info "Verifying nbpy installation..."
    
    if ! ${VENV_PYTHON} -c "from nbpy.zmq import BasePublisher, BaseSubscriber" 2>/dev/null; then
        log_warning "nbpy not installed in development mode"
        log_info "Installing nbpy in development mode..."
        cd "${SCRIPT_DIR}"
        ${VENV_PIP} install -e . --quiet
        log_success "nbpy installed successfully"
    else
        log_success "nbpy module verified"
    fi
}

################################################################################
# Docker Services Management
################################################################################

start_docker_services() {
    print_header "Starting Docker Services (InfluxDB + Grafana)"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed"
        return 1
    fi
    
    log_info "Starting Docker Compose..."
    cd "${SCRIPT_DIR}"
    
    if docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d; then
        log_success "Docker services started"
        
        # Wait for services to be healthy
        log_info "Waiting for InfluxDB to be healthy..."
        local max_attempts=30
        local attempt=0
        
        while [ ${attempt} -lt ${max_attempts} ]; do
            if curl -s "http://${INFLUXDB_HOST}:${INFLUXDB_PORT}/ping" > /dev/null 2>&1; then
                log_success "InfluxDB is healthy"
                break
            fi
            attempt=$((attempt + 1))
            sleep 2
        done
        
        if [ ${attempt} -eq ${max_attempts} ]; then
            log_warning "InfluxDB health check timeout"
        fi
        
        log_info "Waiting for Grafana to be healthy..."
        local attempt=0
        
        while [ ${attempt} -lt ${max_attempts} ]; do
            if curl -s "http://localhost:${GRAFANA_PORT}/api/health" > /dev/null 2>&1; then
                log_success "Grafana is healthy"
                break
            fi
            attempt=$((attempt + 1))
            sleep 2
        done
        
        if [ ${attempt} -eq ${max_attempts} ]; then
            log_warning "Grafana health check timeout"
        fi
        
        return 0
    else
        log_error "Failed to start Docker services"
        return 1
    fi
}

stop_docker_services() {
    print_header "Stopping Docker Services"
    
    if [ ! -f "${DOCKER_COMPOSE_FILE}" ]; then
        log_warning "docker-compose file not found"
        return 0
    fi
    
    log_info "Stopping Docker Compose..."
    cd "${SCRIPT_DIR}"
    docker-compose -f "${DOCKER_COMPOSE_FILE}" down
    log_success "Docker services stopped"
}

docker_status() {
    if ! command -v docker &> /dev/null; then
        log_warning "Docker is not installed"
        return
    fi
    
    print_header "Docker Services Status"
    docker-compose -f "${DOCKER_COMPOSE_FILE}" ps
}

################################################################################
# Python Publishers Management
################################################################################

start_publishers() {
    print_header "Starting ZMQ Publishers"
    
    if [ ${#ZMQ_PUBLISHERS[@]} -eq 0 ]; then
        log_warning "No publishers configured"
        return
    fi
    
    for publisher in "${ZMQ_PUBLISHERS[@]}"; do
        start_publisher "$publisher"
    done
}

start_publisher() {
    local pub_name="$1"
    local cmd="nbpy-pub-${pub_name}"
    local pid_file="${PID_DIR}/pub_${pub_name}.pid"
    local log_file="${LOG_DIR}/pub_${pub_name}.log"
    
    log_info "Starting publisher: ${cmd}"
    
    # Check if already running
    if [ -f "${pid_file}" ]; then
        local old_pid=$(cat "${pid_file}")
        if kill -0 "${old_pid}" 2>/dev/null; then
            log_warning "Publisher ${pub_name} already running (PID: ${old_pid})"
            return
        fi
    fi
    
    # Start in background
    nohup ${VENV_PYTHON} -m nbpy.zmq.publishers.${pub_name//-/_} \
        > "${log_file}" 2>&1 &
    
    local new_pid=$!
    echo ${new_pid} > "${pid_file}"
    log_success "Started ${cmd} (PID: ${new_pid})"
}

stop_publishers() {
    print_header "Stopping ZMQ Publishers"
    
    for pid_file in "${PID_DIR}"/pub_*.pid; do
        if [ -f "${pid_file}" ]; then
            local pid=$(cat "${pid_file}")
            local name=$(basename "${pid_file}" .pid | sed 's/pub_//')
            
            if kill -0 "${pid}" 2>/dev/null; then
                log_info "Stopping ${name} (PID: ${pid})"
                kill "${pid}" 2>/dev/null || true
                sleep 1
                kill -9 "${pid}" 2>/dev/null || true
                rm "${pid_file}"
                log_success "Stopped ${name}"
            fi
        fi
    done
}

publishers_status() {
    print_header "ZMQ Publishers Status"
    
    if [ ! -d "${PID_DIR}" ] || [ -z "$(ls -A ${PID_DIR}/pub_*.pid 2>/dev/null)" ]; then
        log_info "No publishers running"
        return
    fi
    
    for pid_file in "${PID_DIR}"/pub_*.pid; do
        if [ -f "${pid_file}" ]; then
            local pid=$(cat "${pid_file}")
            local name=$(basename "${pid_file}" .pid | sed 's/pub_//')
            
            if kill -0 "${pid}" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} ${name} (PID: ${pid})"
            else
                echo -e "${RED}✗${NC} ${name} (PID: ${pid}) - NOT RUNNING"
            fi
        fi
    done
}

################################################################################
# Python Subscribers Management
################################################################################

start_subscribers() {
    print_header "Starting ZMQ Subscribers"
    
    if [ ${#ZMQ_SUBSCRIBERS[@]} -eq 0 ]; then
        log_warning "No subscribers configured"
        return
    fi
    
    for subscriber in "${ZMQ_SUBSCRIBERS[@]}"; do
        start_subscriber "$subscriber"
    done
}

start_subscriber() {
    local sub_name="$1"
    local cmd="nbpy-sub-${sub_name}"
    local pid_file="${PID_DIR}/sub_${sub_name}.pid"
    local log_file="${LOG_DIR}/sub_${sub_name}.log"
    
    log_info "Starting subscriber: ${cmd}"
    
    # Check if already running
    if [ -f "${pid_file}" ]; then
        local old_pid=$(cat "${pid_file}")
        if kill -0 "${old_pid}" 2>/dev/null; then
            log_warning "Subscriber ${sub_name} already running (PID: ${old_pid})"
            return
        fi
    fi
    
    # Wait for publishers to start
    sleep 2
    
    # Start in background
    nohup ${VENV_PYTHON} -m nbpy.zmq.subscribers.${sub_name//-/_} \
        > "${log_file}" 2>&1 &
    
    local new_pid=$!
    echo ${new_pid} > "${pid_file}"
    log_success "Started ${cmd} (PID: ${new_pid})"
}

stop_subscribers() {
    print_header "Stopping ZMQ Subscribers"
    
    for pid_file in "${PID_DIR}"/sub_*.pid; do
        if [ -f "${pid_file}" ]; then
            local pid=$(cat "${pid_file}")
            local name=$(basename "${pid_file}" .pid | sed 's/sub_//')
            
            if kill -0 "${pid}" 2>/dev/null; then
                log_info "Stopping ${name} (PID: ${pid})"
                kill "${pid}" 2>/dev/null || true
                sleep 1
                kill -9 "${pid}" 2>/dev/null || true
                rm "${pid_file}"
                log_success "Stopped ${name}"
            fi
        fi
    done
}

subscribers_status() {
    print_header "ZMQ Subscribers Status"
    
    if [ ! -d "${PID_DIR}" ] || [ -z "$(ls -A ${PID_DIR}/sub_*.pid 2>/dev/null)" ]; then
        log_info "No subscribers running"
        return
    fi
    
    for pid_file in "${PID_DIR}"/sub_*.pid; do
        if [ -f "${pid_file}" ]; then
            local pid=$(cat "${pid_file}")
            local name=$(basename "${pid_file}" .pid | sed 's/sub_//')
            
            if kill -0 "${pid}" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} ${name} (PID: ${pid})"
            else
                echo -e "${RED}✗${NC} ${name} (PID: ${pid}) - NOT RUNNING"
            fi
        fi
    done
}

################################################################################
# Log Management
################################################################################

show_logs() {
    print_header "Service Logs"
    
    if [ ! -d "${LOG_DIR}" ] || [ -z "$(ls -A ${LOG_DIR}/*.log 2>/dev/null)" ]; then
        log_warning "No logs available"
        return
    fi
    
    tail -f "${LOG_DIR}"/*.log 2>/dev/null || log_warning "No log files found"
}

show_log_summary() {
    print_header "Recent Log Summary"
    
    if [ ! -d "${LOG_DIR}" ]; then
        log_warning "Log directory not found"
        return
    fi
    
    for log_file in "${LOG_DIR}"/*.log; do
        if [ -f "${log_file}" ]; then
            local filename=$(basename "${log_file}")
            echo -e "\n${BLUE}=== ${filename} ===${NC}"
            tail -5 "${log_file}" 2>/dev/null || echo "No content"
        fi
    done
}

################################################################################
# Configuration & Status Display
################################################################################

show_configuration() {
    print_header "NBPY Configuration"
    
    cat << EOF
${BLUE}Installation:${NC}
  Script Directory:   ${SCRIPT_DIR}
  Python Binary:      ${VENV_PYTHON}
  Log Directory:      ${LOG_DIR}
  PID Directory:      ${PID_DIR}

${BLUE}Docker Services:${NC}
  InfluxDB:
    - URL:            http://${INFLUXDB_HOST}:${INFLUXDB_PORT}
    - Web UI:         http://${INFLUXDB_HOST}:8083
    - Default DB:     tick
    - User:           zmq / zmq
  
  Grafana:
    - URL:            http://localhost:${GRAFANA_PORT}
    - User:           admin / admin123
    - Data Source:    InfluxDB

${BLUE}ZMQ Configuration:${NC}
  Framework Path:     ${SCRIPT_DIR}/nbpy/zmq
  Port Registry:      ${SCRIPT_DIR}/nbpy/zmq/ports.py
  Base Classes:       ${SCRIPT_DIR}/nbpy/zmq/base.py

${BLUE}Configured Publishers (${#ZMQ_PUBLISHERS[@]}):${NC}
EOF
    
    for pub in "${ZMQ_PUBLISHERS[@]}"; do
        echo "  - nbpy-pub-${pub}"
    done
    
    cat << EOF

${BLUE}Configured Subscribers (${#ZMQ_SUBSCRIBERS[@]}):${NC}
EOF
    
    for sub in "${ZMQ_SUBSCRIBERS[@]}"; do
        echo "  - nbpy-sub-${sub}"
    done
    
    cat << EOF

${BLUE}Documentation:${NC}
  Service Index:      ${SCRIPT_DIR}/nbpy/zmq/SERVICES_INDEX.md
  Migration Report:   ${SCRIPT_DIR}/nbpy/zmq/MIGRATION_COMPLETE.md
  Final Report:       ${SCRIPT_DIR}/ZMQ_MIGRATION_FINAL_REPORT.md

EOF
}

show_status() {
    print_header "Overall Service Status"
    
    # Docker status
    if command -v docker &> /dev/null; then
        echo -e "\n${BLUE}Docker Services:${NC}"
        docker-compose -f "${DOCKER_COMPOSE_FILE}" ps 2>/dev/null || echo "Docker Compose not available"
    fi
    
    # Python services status
    publishers_status
    subscribers_status
    
    # Port availability
    echo ""
    echo -e "${BLUE}Port Status:${NC}"
    
    if nc -z localhost ${INFLUXDB_PORT} 2>/dev/null; then
        echo -e "${GREEN}✓${NC} InfluxDB (${INFLUXDB_PORT})"
    else
        echo -e "${RED}✗${NC} InfluxDB (${INFLUXDB_PORT})"
    fi
    
    if nc -z localhost ${GRAFANA_PORT} 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Grafana (${GRAFANA_PORT})"
    else
        echo -e "${RED}✗${NC} Grafana (${GRAFANA_PORT})"
    fi
}

open_dashboards() {
    print_header "Opening Dashboards"
    
    log_info "Opening Grafana dashboard..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:${GRAFANA_PORT}" &
    elif command -v open &> /dev/null; then
        open "http://localhost:${GRAFANA_PORT}" &
    else
        log_warning "Please open http://localhost:${GRAFANA_PORT} in your browser"
    fi
    
    log_info "Opening InfluxDB UI..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://${INFLUXDB_HOST}:8083" &
    elif command -v open &> /dev/null; then
        open "http://${INFLUXDB_HOST}:8083" &
    else
        log_warning "Please open http://${INFLUXDB_HOST}:8083 in your browser"
    fi
}

################################################################################
# Main Command Handler
################################################################################

main() {
    local cmd="${1:-help}"
    
    case "${cmd}" in
        start)
            print_header "Starting NBPY ZMQ Services"
            setup_directories
            verify_venv
            verify_nbpy_installation
            start_docker_services
            sleep 3
            start_publishers
            sleep 2
            start_subscribers
            sleep 1
            open_dashboards
            show_status
            log_success "All services started successfully!"
            ;;
        
        stop)
            print_header "Stopping NBPY ZMQ Services"
            stop_subscribers
            stop_publishers
            stop_docker_services
            log_success "All services stopped"
            ;;
        
        restart)
            print_header "Restarting NBPY ZMQ Services"
            $0 stop
            sleep 2
            $0 start
            ;;
        
        status)
            show_status
            ;;
        
        logs)
            show_logs
            ;;
        
        logsummary)
            show_log_summary
            ;;
        
        config)
            show_configuration
            ;;
        
        open)
            open_dashboards
            ;;
        
        docker-logs)
            print_header "Docker Service Logs"
            docker-compose -f "${DOCKER_COMPOSE_FILE}" logs -f
            ;;
        
        *)
            cat << EOF

${BLUE}NBPY ZMQ Microservices Startup Script${NC}

${BLUE}Usage:${NC}
  $0 [command]

${BLUE}Commands:${NC}
  start          Start all services (Docker + Python)
  stop           Stop all services
  restart        Restart all services
  status         Show service status
  config         Show configuration
  logs           Follow service logs
  logsummary     Show recent log summary
  open           Open dashboards in browser
  docker-logs    Follow Docker Compose logs
  help           Show this help message

${BLUE}Examples:${NC}
  # Start everything
  $0 start

  # Check status
  $0 status

  # View logs
  $0 logs

  # Stop services
  $0 stop

${BLUE}Services Started:${NC}
  - InfluxDB (http://localhost:8086)
  - Grafana (http://localhost:3000)
  - ${#ZMQ_PUBLISHERS[@]} ZMQ Publishers
  - ${#ZMQ_SUBSCRIBERS[@]} ZMQ Subscribers

${BLUE}Default Credentials:${NC}
  Grafana:  admin / admin123
  InfluxDB: zmq / zmq

${BLUE}Documentation:${NC}
  See SERVICES_INDEX.md for complete service reference
  See ZMQ_MIGRATION_FINAL_REPORT.md for technical details

EOF
            ;;
    esac
}

# Run main function
main "$@"
