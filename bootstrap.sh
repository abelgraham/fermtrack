#!/bin/bash

#
# FermTrack - Fermentation Tracking System - Bootstrap Script
# Copyright (C) 2026 FermTrack Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

#===============================================================================
# FermTrack Bootstrap Script
#
# Quick start script for running FermTrack development servers
#
# Usage:
#   ./bootstrap.sh              # Start both servers
#   ./bootstrap.sh backend      # Start only backend
#   ./bootstrap.sh frontend     # Start only frontend  
#   ./bootstrap.sh stop         # Stop all running servers
#   ./bootstrap.sh status       # Check server status
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=5000
FRONTEND_PORT=8080
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PIDFILE_DIR="$PROJECT_ROOT/.pids"

# Create PID directory if it doesn't exist
mkdir -p "$PIDFILE_DIR"

# Print colored output
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Get process ID from PID file
get_pid() {
    local service=$1
    local pidfile="$PIDFILE_DIR/${service}.pid"
    if [[ -f "$pidfile" ]]; then
        cat "$pidfile"
    fi
}

# Check if service is running
is_running() {
    local service=$1
    local pid=$(get_pid "$service")
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        return 0  # Running
    else
        return 1  # Not running
    fi
}

# Start backend server
start_backend() {
    log_info "Starting FermTrack Backend API..."
    
    if is_running "backend"; then
        log_warn "Backend is already running (PID: $(get_pid 'backend'))"
        return 0
    fi
    
    if check_port $BACKEND_PORT; then
        log_error "Port $BACKEND_PORT is already in use by another process"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if Python requirements are installed
    if ! python3 -c "import flask" 2>/dev/null; then
        log_info "Installing backend dependencies..."
        python3 -m pip install -r requirements.txt
    fi
    
    # Start backend server in background
    log_info "Launching backend server on port $BACKEND_PORT..."
    nohup python3 app.py > "$PIDFILE_DIR/backend.log" 2>&1 &
    local pid=$!
    echo $pid > "$PIDFILE_DIR/backend.pid"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if is_running "backend"; then
        log_success "Backend API started successfully (PID: $pid)"
        log_info "API available at: http://localhost:$BACKEND_PORT"
        return 0
    else
        log_error "Failed to start backend server"
        return 1
    fi
}

# Start frontend server
start_frontend() {
    log_info "Starting FermTrack Frontend..."
    
    if is_running "frontend"; then
        log_warn "Frontend is already running (PID: $(get_pid 'frontend'))"
        return 0
    fi
    
    if check_port $FRONTEND_PORT; then
        log_error "Port $FRONTEND_PORT is already in use by another process"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Start frontend server in background
    log_info "Launching frontend server on port $FRONTEND_PORT..."
    nohup python3 serve.py > "$PIDFILE_DIR/frontend.log" 2>&1 &
    local pid=$!
    echo $pid > "$PIDFILE_DIR/frontend.pid"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if is_running "frontend"; then
        log_success "Frontend server started successfully (PID: $pid)"
        log_info "Web app available at: http://localhost:$FRONTEND_PORT"
        return 0
    else
        log_error "Failed to start frontend server"
        return 1
    fi
}

# Stop service
stop_service() {
    local service=$1
    local pid=$(get_pid "$service")
    
    if [[ -z "$pid" ]]; then
        log_warn "$service is not running (no PID file)"
        return 0
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        log_info "Stopping $service (PID: $pid)..."
        kill $pid
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$pid" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "Force killing $service..."
            kill -9 "$pid"
        fi
        
        log_success "$service stopped"
    else
        log_warn "$service was not running"
    fi
    
    # Clean up PID file
    rm -f "$PIDFILE_DIR/${service}.pid"
}

# Stop all services
stop_all() {
    log_info "Stopping FermTrack servers..."
    stop_service "backend"
    stop_service "frontend"
    log_success "All services stopped"
}

# Show status
show_status() {
    echo -e "${BLUE}📊 FermTrack Server Status${NC}"
    echo "================================"
    
    # Backend status
    if is_running "backend"; then
        echo -e "Backend API:   ${GREEN}RUNNING${NC} (PID: $(get_pid 'backend'), Port: $BACKEND_PORT)"
    else
        echo -e "Backend API:   ${RED}STOPPED${NC}"
    fi
    
    # Frontend status  
    if is_running "frontend"; then
        echo -e "Frontend Web:  ${GREEN}RUNNING${NC} (PID: $(get_pid 'frontend'), Port: $FRONTEND_PORT)"
    else
        echo -e "Frontend Web:  ${RED}STOPPED${NC}"
    fi
    
    echo ""
    
    # URLs
    if is_running "backend" || is_running "frontend"; then
        echo -e "${BLUE}🌐 Access URLs:${NC}"
        if is_running "frontend"; then
            echo "   Web App: http://localhost:$FRONTEND_PORT"
        fi
        if is_running "backend"; then
            echo "   API:     http://localhost:$BACKEND_PORT"
        fi
        echo ""
    fi
    
    # Log files
    echo -e "${BLUE}📝 Log Files:${NC}"
    echo "   Backend:  $PIDFILE_DIR/backend.log"
    echo "   Frontend: $PIDFILE_DIR/frontend.log"
}

# Show help
show_help() {
    echo "FermTrack Bootstrap Script"
    echo "========================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  <none>      Start both backend and frontend servers"
    echo "  backend     Start only the backend API server"
    echo "  frontend    Start only the frontend web server"
    echo "  stop        Stop all running servers"
    echo "  status      Show server status"
    echo "  logs        Show recent log output"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./bootstrap.sh              # Start full application"
    echo "  ./bootstrap.sh backend      # Start only API"
    echo "  ./bootstrap.sh stop         # Stop everything"
    echo ""
}

# Show logs
show_logs() {
    echo -e "${BLUE}📝 Recent Logs${NC}"
    echo "==============="
    
    if [[ -f "$PIDFILE_DIR/backend.log" ]]; then
        echo -e "\n${GREEN}Backend Log:${NC}"
        tail -20 "$PIDFILE_DIR/backend.log"
    fi
    
    if [[ -f "$PIDFILE_DIR/frontend.log" ]]; then
        echo -e "\n${GREEN}Frontend Log:${NC}"
        tail -20 "$PIDFILE_DIR/frontend.log"
    fi
}

# Main script logic
main() {
    local command=${1:-"start"}
    
    echo -e "${BLUE}🚀 FermTrack Bootstrap${NC}"
    echo "======================"
    
    case "$command" in
        "start" | "")
            start_backend && start_frontend
            if is_running "backend" && is_running "frontend"; then
                echo ""
                log_success "FermTrack is now running!"
                echo ""
                show_status
            fi
            ;;
        "backend")
            start_backend
            ;;
        "frontend")
            start_frontend
            ;;
        "stop")
            stop_all
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "help" | "-h" | "--help")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Received interrupt signal...${NC}"; stop_all; exit 0' INT TERM

# Run main function
main "$@"