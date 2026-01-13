#!/bin/bash

################################################################################
#                                                                              #
#           NBPY INTEGRATED ZMQ MICROSERVICES ORCHESTRATION SYSTEM             #
#                                                                              #
# This script provides complete orchestration of:                            #
#   1. Docker containers (InfluxDB + Grafana)                                #
#   2. InfluxDB retention policies                                           #
#   3. ZMQ publishers (data sources)                                         #
#   4. ZMQ subscribers (data sinks)                                          #
#   5. Grafana dashboard provisioning                                        #
#   6. Message streaming validation                                          #
#   7. Health monitoring and graceful shutdown                               #
#                                                                              #
# Usage:                                                                       #
#   ./integrated_startup.sh start   - Start entire system                    #
#   ./integrated_startup.sh stop    - Stop entire system gracefully          #
#   ./integrated_startup.sh restart - Restart entire system                  #
#   ./integrated_startup.sh status  - Show system status                     #
#   ./integrated_startup.sh validate- Validate message streaming             #
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
INTEGRATION_CONFIG="${SCRIPT_DIR}/integration_config.json"
STARTUP_LOG="${LOG_DIR}/integrated_startup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Timing constants
DOCKER_STARTUP_WAIT=15
RETENTION_SETUP_WAIT=5
PUBLISHERS_STARTUP_WAIT=3
SUBSCRIBERS_STARTUP_WAIT=3
GRAFANA_SETUP_WAIT=5
VALIDATION_WAIT=15

################################################################################
# Utility Functions
################################################################################

log_info() {
    local msg="$1"
    echo -e "${BLUE}[INFO]${NC} ${msg}" | tee -a "${STARTUP_LOG}"
}

log_success() {
    local msg="$1"
    echo -e "${GREEN}[✓]${NC} ${msg}" | tee -a "${STARTUP_LOG}"
}

log_error() {
    local msg="$1"
    echo -e "${RED}[✗]${NC} ${msg}" | tee -a "${STARTUP_LOG}" >&2
}

log_warning() {
    local msg="$1"
    echo -e "${YELLOW}[!]${NC} ${msg}" | tee -a "${STARTUP_LOG}"
}

log_phase() {
    local phase="$1"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${MAGENTA}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "${MAGENTA}PHASE: ${phase}${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "${MAGENTA}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
}

log_divider() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
}

setup_directories() {
    mkdir -p "${LOG_DIR}"
    mkdir -p "${PID_DIR}"
    chmod 755 "${LOG_DIR}" "${PID_DIR}"
}

verify_requirements() {
    log_info "Verifying system requirements..."
    
    local missing_tools=0
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Docker found"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed"
        missing_tools=$((missing_tools + 1))
    else
        log_success "docker-compose found"
    fi
    
    if [ ! -f "${VENV_PYTHON}" ]; then
        log_error "Python virtual environment not found"
        log_info "Create venv with: python3 -m venv ${SCRIPT_DIR}/nbpy"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Python environment found"
    fi
    
    if [ ! -f "${INTEGRATION_CONFIG}" ]; then
        log_error "Integration config not found: ${INTEGRATION_CONFIG}"
        missing_tools=$((missing_tools + 1))
    else
        log_success "Integration config found"
    fi
    
    if [ ${missing_tools} -gt 0 ]; then
        log_error "Missing ${missing_tools} requirement(s)"
        return 1
    fi
    
    return 0
}

check_port_available() {
    local port=$1
    local name=$2
    
    if nc -z localhost "${port}" 2>/dev/null; then
        log_warning "Port ${port} (${name}) is already in use"
        return 1
    fi
    
    return 0
}

################################################################################
# Phase 1: Docker Containers
################################################################################

start_docker_containers() {
    log_phase "1: Starting Docker Containers (InfluxDB + Grafana)"
    
    log_info "Starting Docker Compose services..."
    cd "${SCRIPT_DIR}"
    
    if ! docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d; then
        log_error "Failed to start Docker services"
        return 1
    fi
    
    log_success "Docker Compose started"
    log_info "Waiting ${DOCKER_STARTUP_WAIT}s for services to initialize..."
    sleep "${DOCKER_STARTUP_WAIT}"
    
    # Check InfluxDB
    log_info "Checking InfluxDB health..."
    local max_attempts=30
    local attempt=0
    
    while [ ${attempt} -lt ${max_attempts} ]; do
        if curl -s "http://localhost:8086/ping" > /dev/null 2>&1; then
            log_success "InfluxDB is healthy"
            break
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    if [ ${attempt} -eq ${max_attempts} ]; then
        log_warning "InfluxDB health check timeout"
    fi
    
    # Check Grafana
    log_info "Checking Grafana health..."
    attempt=0
    
    while [ ${attempt} -lt ${max_attempts} ]; do
        if curl -s "http://localhost:3000/api/health" > /dev/null 2>&1; then
            log_success "Grafana is healthy"
            break
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    if [ ${attempt} -eq ${max_attempts} ]; then
        log_warning "Grafana health check timeout"
    fi
    
    return 0
}

stop_docker_containers() {
    log_phase "Stopping Docker Containers"
    
    log_info "Stopping Docker Compose..."
    cd "${SCRIPT_DIR}"
    
    if docker-compose -f "${DOCKER_COMPOSE_FILE}" down; then
        log_success "Docker services stopped"
        return 0
    else
        log_error "Failed to stop Docker services"
        return 1
    fi
}

################################################################################
# Phase 2: InfluxDB Retention Policies
################################################################################

setup_retention_policies() {
    log_phase "2: Configuring InfluxDB Retention Policies"
    
    log_info "Setting up retention policies and databases..."
    
    if ! "${VENV_PYTHON}" "${SCRIPT_DIR}/db/retention_policy.py" \
        --config "${INTEGRATION_CONFIG}" \
        --host localhost \
        --port 8086 \
        --database tick \
        create; then
        log_error "Failed to setup retention policies"
        return 1
    fi
    
    log_success "Retention policies configured"
    log_info "Waiting ${RETENTION_SETUP_WAIT}s..."
    sleep "${RETENTION_SETUP_WAIT}"
    
    return 0
}

################################################################################
# Phase 3: ZMQ Publishers
################################################################################

start_publishers() {
    log_phase "3: Starting ZMQ Publishers"
    
    log_info "Starting all enabled publishers..."
    
    if ! "${VENV_PYTHON}" "${SCRIPT_DIR}/db/service_manager.py" \
        --config "${INTEGRATION_CONFIG}" \
        start; then
        log_error "Service manager failed to start publishers"
        return 1
    fi
    
    log_success "Publishers started"
    log_info "Waiting ${PUBLISHERS_STARTUP_WAIT}s..."
    sleep "${PUBLISHERS_STARTUP_WAIT}"
    
    return 0
}

################################################################################
# Phase 4: Grafana Setup
################################################################################

setup_grafana() {
    log_phase "4: Provisioning Grafana Dashboards"
    
    log_info "Configuring Grafana datasources and dashboards..."
    log_info "Waiting ${GRAFANA_SETUP_WAIT}s for Grafana to be ready..."
    sleep "${GRAFANA_SETUP_WAIT}"
    
    if ! "${VENV_PYTHON}" "${SCRIPT_DIR}/db/grafana_setup.py" \
        --config "${INTEGRATION_CONFIG}" \
        setup; then
        log_warning "Grafana setup had issues (non-critical)"
    else
        log_success "Grafana dashboards provisioned"
    fi
    
    return 0
}

################################################################################
# Phase 5: Message Validation
################################################################################

validate_message_streaming() {
    log_phase "5: Validating Message Streaming"
    
    log_info "Starting message flow validation..."
    log_info "Monitoring ZMQ topics for ${VALIDATION_WAIT}s..."
    
    if ! "${VENV_PYTHON}" "${SCRIPT_DIR}/db/message_validator.py" \
        --config "${INTEGRATION_CONFIG}" \
        --duration "${VALIDATION_WAIT}" \
        full; then
        log_warning "Message validation had issues"
        return 1
    fi
    
    log_success "Message validation passed"
    return 0
}

################################################################################
# Status and Display
################################################################################

show_status() {
    log_divider
    echo "" | tee -a "${STARTUP_LOG}"
    
    log_info "Checking Docker containers..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" ps | tee -a "${STARTUP_LOG}"
    
    echo "" | tee -a "${STARTUP_LOG}"
    
    log_info "Showing ZMQ service status..."
    "${VENV_PYTHON}" "${SCRIPT_DIR}/db/service_manager.py" \
        --config "${INTEGRATION_CONFIG}" \
        status | tee -a "${STARTUP_LOG}"
    
    log_divider
}

print_access_info() {
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "${GREEN}✓ SYSTEM STARTUP COMPLETE${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${CYAN}Access Points:${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "  ${CYAN}InfluxDB API${NC}        → http://localhost:8086" | tee -a "${STARTUP_LOG}"
    echo -e "  ${CYAN}Grafana UI${NC}          → http://localhost:3000" | tee -a "${STARTUP_LOG}"
    echo -e "                       (admin / admin123)" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${CYAN}ZMQ Services:${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "  ${CYAN}Publishers${NC}          → Streaming data on configured topics" | tee -a "${STARTUP_LOG}"
    echo -e "  ${CYAN}Subscribers${NC}         → Forwarding to InfluxDB" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${CYAN}Documentation:${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "  ${CYAN}Startup Log${NC}         → ${STARTUP_LOG}" | tee -a "${STARTUP_LOG}"
    echo -e "  ${CYAN}Config${NC}              → ${INTEGRATION_CONFIG}" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
}

print_error_info() {
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "${RED}✗ SYSTEM STARTUP FAILED${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${YELLOW}Check the following:${NC}" | tee -a "${STARTUP_LOG}"
    echo -e "  1. Startup log: ${STARTUP_LOG}" | tee -a "${STARTUP_LOG}"
    echo -e "  2. Docker logs: docker-compose -f ${DOCKER_COMPOSE_FILE} logs" | tee -a "${STARTUP_LOG}"
    echo -e "  3. Service logs: ls -la ${LOG_DIR}/" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}" | tee -a "${STARTUP_LOG}"
    echo "" | tee -a "${STARTUP_LOG}"
}

################################################################################
# Signal Handlers for Graceful Shutdown
################################################################################

cleanup() {
    log_info "Received shutdown signal, initiating graceful shutdown..."
    echo "" | tee -a "${STARTUP_LOG}"
    stop_system
}

trap cleanup SIGINT SIGTERM

################################################################################
# Main Functions
################################################################################

start_system() {
    log_divider
    echo -e "${MAGENTA}STARTING NBPY INTEGRATED SYSTEM${NC}" | tee -a "${STARTUP_LOG}"
    log_divider
    
    setup_directories
    
    if ! verify_requirements; then
        log_error "System requirements not met"
        return 1
    fi
    
    if ! start_docker_containers; then
        log_error "Docker container startup failed"
        print_error_info
        return 1
    fi
    
    if ! setup_retention_policies; then
        log_error "Retention policy setup failed"
        print_error_info
        return 1
    fi
    
    if ! start_publishers; then
        log_error "Publisher startup failed"
        print_error_info
        return 1
    fi
    
    if ! setup_grafana; then
        log_warning "Grafana setup had issues (continuing)"
    fi
    
    log_info "Waiting before validation..."
    sleep 5
    
    if ! validate_message_streaming; then
        log_warning "Message validation failed (check logs)"
    fi
    
    show_status
    print_access_info
    
    log_success "System startup complete"
    return 0
}

stop_system() {
    log_divider
    echo -e "${MAGENTA}STOPPING NBPY INTEGRATED SYSTEM${NC}" | tee -a "${STARTUP_LOG}"
    log_divider
    
    setup_directories
    
    log_phase "Graceful Shutdown: Stopping Services"
    
    log_info "Stopping service manager..."
    "${VENV_PYTHON}" "${SCRIPT_DIR}/db/service_manager.py" \
        --config "${INTEGRATION_CONFIG}" \
        stop --timeout 30 || true
    
    sleep 3
    
    log_info "Stopping Docker containers..."
    stop_docker_containers || true
    
    log_success "System stopped"
    return 0
}

restart_system() {
    stop_system
    sleep 3
    start_system
}

validate_only() {
    setup_directories
    
    if ! verify_requirements; then
        log_error "System requirements not met"
        return 1
    fi
    
    validate_message_streaming
}

################################################################################
# Command Line Interface
################################################################################

case "${1:-start}" in
    start)
        start_system
        ;;
    stop)
        stop_system
        ;;
    restart)
        restart_system
        ;;
    status)
        show_status
        ;;
    validate)
        validate_only
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|validate}"
        echo ""
        echo "Commands:"
        echo "  start     - Start entire integrated system"
        echo "  stop      - Stop entire system gracefully"
        echo "  restart   - Restart entire system"
        echo "  status    - Show system status"
        echo "  validate  - Validate message streaming (requires system running)"
        exit 1
        ;;
esac

exit $?
