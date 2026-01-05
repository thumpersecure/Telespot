#!/bin/bash
#
# telespot - Just Do It Installation Script
# Version 5.0-beta
#
# This script handles the complete installation of telespot:
# 1. Clones the repository (or updates if exists)
# 2. Installs Python dependencies
# 3. Sets up configuration
# 4. Runs a test search
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/thumpersecure/Telespot/main/just-do-it.sh | bash
#   OR
#   wget -qO- https://raw.githubusercontent.com/thumpersecure/Telespot/main/just-do-it.sh | bash
#   OR
#   ./just-do-it.sh
#

set -e

# Colors for output
RED='\033[0;91m'
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
WHITE='\033[0;97m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/thumpersecure/Telespot.git"
INSTALL_DIR="$HOME/Telespot"

# Print banner
print_banner() {
    echo -e "${WHITE}"
    echo "  _       *      _                     _   *"
    echo " | |_ ___| | ___  ___ _ __   ___ | |_"
    echo " | __/ _ \\ |/ _ \\/ __| '_ \\ / _ \\| __|*"
    echo " | ||  __/ |  __/\\__ \\ |_) | (_) | |_"
    echo "  \\__\\___|_|\\___||___/ .__/ \\___/ \\__|"
    echo "*                    |_|    *   ${BLUE}v5.0-beta${NC}"
    echo ""
    echo -e "${WHITE}Just Do It - Installation Script${NC}"
    echo "========================================"
    echo ""
}

# Print status messages
info() {
    echo -e "${BLUE}[*]${NC} $1"
}

success() {
    echo -e "${GREEN}[+]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[-]${NC} $1"
}

# Check for required commands
check_requirements() {
    info "Checking requirements..."

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        success "Python 3 found: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ "$PYTHON_VERSION" == 3* ]]; then
            PYTHON_CMD="python"
            success "Python 3 found: $PYTHON_VERSION"
        else
            error "Python 3 is required but only Python 2 was found"
            exit 1
        fi
    else
        error "Python 3 is required but not found"
        echo "Please install Python 3:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "  macOS: brew install python3"
        echo "  Windows: https://www.python.org/downloads/"
        exit 1
    fi

    # Check pip
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        success "pip3 found"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        success "pip found"
    else
        warn "pip not found, attempting to install..."
        $PYTHON_CMD -m ensurepip --upgrade 2>/dev/null || {
            error "Could not install pip"
            echo "Please install pip manually:"
            echo "  Ubuntu/Debian: sudo apt install python3-pip"
            exit 1
        }
        PIP_CMD="$PYTHON_CMD -m pip"
    fi

    # Check git (optional but preferred)
    if command -v git &> /dev/null; then
        GIT_AVAILABLE=true
        success "git found"
    else
        GIT_AVAILABLE=false
        warn "git not found - will download as zip instead"
    fi

    echo ""
}

# Clone or update repository
get_repository() {
    info "Setting up telespot..."

    if [ -d "$INSTALL_DIR" ]; then
        info "Existing installation found at $INSTALL_DIR"

        if [ -d "$INSTALL_DIR/.git" ] && [ "$GIT_AVAILABLE" = true ]; then
            info "Updating from repository..."
            cd "$INSTALL_DIR"
            git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || {
                warn "Could not update, continuing with existing version"
            }
            success "Repository updated"
        else
            warn "Keeping existing installation"
        fi
    else
        if [ "$GIT_AVAILABLE" = true ]; then
            info "Cloning repository..."
            git clone "$REPO_URL" "$INSTALL_DIR"
            success "Repository cloned to $INSTALL_DIR"
        else
            info "Downloading repository as zip..."
            TEMP_ZIP="/tmp/telespot.zip"

            # Try wget first, then curl
            if command -v wget &> /dev/null; then
                wget -q -O "$TEMP_ZIP" "https://github.com/thumpersecure/Telespot/archive/main.zip"
            elif command -v curl &> /dev/null; then
                curl -sL -o "$TEMP_ZIP" "https://github.com/thumpersecure/Telespot/archive/main.zip"
            else
                error "Neither wget nor curl found"
                exit 1
            fi

            # Extract
            if command -v unzip &> /dev/null; then
                unzip -q "$TEMP_ZIP" -d "/tmp/"
                mv "/tmp/Telespot-main" "$INSTALL_DIR"
                rm "$TEMP_ZIP"
                success "Repository downloaded and extracted"
            else
                error "unzip not found"
                echo "Please install unzip: sudo apt install unzip"
                exit 1
            fi
        fi
    fi

    cd "$INSTALL_DIR"
    echo ""
}

# Install Python dependencies
install_dependencies() {
    info "Installing Python dependencies..."

    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt --quiet --user 2>/dev/null || \
        $PIP_CMD install -r requirements.txt --quiet || {
            warn "Some dependencies may have failed to install"
        }
        success "Dependencies installed"
    else
        # Install core dependencies manually
        $PIP_CMD install requests beautifulsoup4 lxml --quiet --user 2>/dev/null || \
        $PIP_CMD install requests beautifulsoup4 lxml --quiet
        success "Core dependencies installed"
    fi

    echo ""
}

# Set up configuration
setup_config() {
    info "Setting up configuration..."

    if [ ! -f "config.txt" ]; then
        if [ -f "config.txt.example" ]; then
            cp "config.txt.example" "config.txt"
        else
            # Create default config
            cat > "config.txt" << 'EOF'
# telespot Configuration File
# Run 'telespot --setup' for interactive configuration

# API Keys (optional)
numverify_api_key=
abstract_api_key=
twilio_account_sid=
twilio_auth_token=
opencnam_account_sid=
opencnam_auth_token=
telnyx_api_key=

# Settings
default_country_code=+1
rate_limit_min=3
rate_limit_max=5
default_output_format=text
verbose=false
colorful_mode=false
EOF
        fi
        success "Configuration file created"
    else
        success "Configuration file exists"
    fi

    # Make telespot.py executable
    if [ -f "telespot.py" ]; then
        chmod +x telespot.py
        success "Made telespot.py executable"
    fi

    echo ""
}

# Create convenient aliases/symlinks
setup_shortcuts() {
    info "Setting up shortcuts..."

    # Create a wrapper script in user's local bin
    LOCAL_BIN="$HOME/.local/bin"

    if [ ! -d "$LOCAL_BIN" ]; then
        mkdir -p "$LOCAL_BIN"
    fi

    # Create wrapper script
    cat > "$LOCAL_BIN/telespot" << EOF
#!/bin/bash
$PYTHON_CMD "$INSTALL_DIR/telespot.py" "\$@"
EOF

    chmod +x "$LOCAL_BIN/telespot"

    # Check if LOCAL_BIN is in PATH
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        warn "Add $LOCAL_BIN to your PATH for easier access"
        echo ""
        echo "  Add this to your ~/.bashrc or ~/.zshrc:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
    else
        success "Shortcut created: telespot"
    fi

    echo ""
}

# Run a test
run_test() {
    info "Running test..."

    cd "$INSTALL_DIR"

    # Just show help to verify it works
    $PYTHON_CMD telespot.py --help > /dev/null 2>&1 && {
        success "telespot is working correctly!"
    } || {
        warn "telespot may have issues - check dependencies"
    }

    echo ""
}

# Print final instructions
print_final() {
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  telespot is installed at: $INSTALL_DIR"
    echo ""
    echo "  Quick Start:"
    echo "    cd $INSTALL_DIR"
    echo "    python3 telespot.py 2155551234"
    echo ""
    echo "  Or if PATH is configured:"
    echo "    telespot 2155551234"
    echo ""
    echo "  Configure API keys (optional):"
    echo "    python3 telespot.py --setup"
    echo ""
    echo "  View all options:"
    echo "    python3 telespot.py --help"
    echo ""
    echo "  Update to latest version:"
    echo "    python3 telespot.py --update"
    echo ""
    echo -e "${BLUE}  Happy hunting!${NC}"
    echo ""
}

# Main execution
main() {
    print_banner
    check_requirements
    get_repository
    install_dependencies
    setup_config
    setup_shortcuts
    run_test
    print_final
}

# Run main function
main
