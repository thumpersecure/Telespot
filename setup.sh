#!/bin/bash
#
# TeleSpot Quick Setup Script
# Automates virtual environment creation and dependency installation
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << "EOF"
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                            Quick Setup Script v4.5
EOF
echo -e "${NC}\n"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   TeleSpot Installation${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo -e "${YELLOW}Please install Python 3.6 or higher and try again.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"

# Create virtual environment
VENV_DIR="telespot-env"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}! Virtual environment already exists at ${VENV_DIR}${NC}"
    read -p "Do you want to remove it and create a fresh one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${CYAN}Using existing virtual environment...${NC}"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${CYAN}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${CYAN}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install requirements
if [ -f "requirements.txt" ]; then
    echo -e "${CYAN}Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}! requirements.txt not found${NC}"
    echo -e "${CYAN}Installing ddgr directly...${NC}"
    pip install ddgr
    echo -e "${GREEN}✓ ddgr installed${NC}"
fi

# Make telespot.py executable
if [ -f "telespot.py" ]; then
    chmod +x telespot.py
    echo -e "${GREEN}✓ telespot.py is now executable${NC}"
else
    echo -e "${YELLOW}! telespot.py not found in current directory${NC}"
fi

# Installation complete
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}   Installation Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${CYAN}To use TeleSpot:${NC}\n"
echo -e "  1. Activate the virtual environment:"
echo -e "     ${YELLOW}source ${VENV_DIR}/bin/activate${NC}\n"
echo -e "  2. Run TeleSpot:"
echo -e "     ${YELLOW}./telespot.py${NC}"
echo -e "     or"
echo -e "     ${YELLOW}python telespot.py 5555551212${NC}\n"
echo -e "  3. When done, deactivate the environment:"
echo -e "     ${YELLOW}deactivate${NC}\n"

echo -e "${BLUE}Quick start:${NC}"
echo -e "${YELLOW}source ${VENV_DIR}/bin/activate && ./telespot.py${NC}\n"

# Ask if user wants to run TeleSpot now
read -p "Would you like to run TeleSpot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "telespot.py" ]; then
        echo -e "\n${CYAN}Launching TeleSpot...${NC}\n"
        python telespot.py
    else
        echo -e "${RED}Error: telespot.py not found${NC}"
    fi
else
    echo -e "${CYAN}Setup complete. Run TeleSpot anytime with:${NC}"
    echo -e "${YELLOW}source ${VENV_DIR}/bin/activate && ./telespot.py${NC}\n"
fi
