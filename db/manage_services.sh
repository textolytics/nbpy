#!/bin/bash
# Docker Service Management Wrapper
# Provides convenient access to service management commands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/manage_services.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: manage_services.py not found in $SCRIPT_DIR"
    exit 1
fi

# Run the Python script with all arguments
python3 "$PYTHON_SCRIPT" "$@"
