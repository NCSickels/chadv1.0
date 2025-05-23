#!/bin/bash
#
#  ██████╗██╗  ██╗ █████╗ ██████╗     ██╗   ██╗ ██╗    ██████╗ 
# ██╔════╝██║  ██║██╔══██╗██╔══██╗    ██║   ██║███║   ██╔═████╗
# ██║     ███████║███████║██║  ██║    ██║   ██║╚██║   ██║██╔██║
# ██║     ██╔══██║██╔══██║██║  ██║    ╚██╗ ██╔╝ ██║   ████╔╝██║
# ╚██████╗██║  ██║██║  ██║██████╔╝     ╚████╔╝  ██║██╗╚██████╔╝
#  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝       ╚═══╝   ╚═╝╚═╝ ╚═════╝ 
#   
#  Charger Active Defense v1.0 Install Script
#  
set -euo pipefail

CHAD_VERSION="1.0"
SCRIPT_VERSION="0.1.0"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the repository URL to the GitHub repository - change if needed. 
REPO_PARENT_URL="https://github.com"
REPO_RAW_URL="https://raw.githubusercontent.com"
REPO_USER="NCSickels"
REPO_BASE="chadv1.0"
REPO_URL="$REPO_PARENT_URL/$REPO_BASE.git"

# Debug mode flag
DEBUG=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color

# Colorized log messages
function log() {
    local level=$1
    local message=$2

    case $level in
        info)
            echo -e "${BLUE}[INFO]${NC} $message" ;;
        warn)
            echo -e "${YELLOW}[WARN]${NC} $message" ;;
        error)
            echo -e "${RED}[ERROR]${NC} $message" ;;
        *)
            echo -e "${WHITE}[LOG]${NC} $message" ;;
    esac
}

function banner() {
    local DARK_BLUE="\033[38;5;20m"
    local DARK_PURPLE="\033[38;5;92m"
    local DARK_RED="\033[38;5;1m"
    local NC='\033[0m' # No Color

    echo -e "\t\t============================================"
    echo -e "${DARK_BLUE}\t\t     ██████╗██╗  ██╗ █████╗ ██████╗${NC}"
    echo -e "${DARK_BLUE}\t\t    ██╔════╝██║  ██║██╔══██╗██╔══██╗${NC}"
    echo -e "${DARK_PURPLE}\t\t    ██║     ███████║███████║██║  ██║${NC}"
    echo -e "${DARK_PURPLE}\t\t    ██║     ██╔══██║██╔══██║██║  ██║${NC}"
    echo -e "${DARK_RED}\t\t    ╚██████╗██║  ██║██║  ██║██████╔╝${NC}"
    echo -e "${DARK_RED}\t\t     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝${NC}"
    echo -e "\t\t============================================"
    echo -e "\t\t      Charger Active Defense v$CHAD_VERSION"
    echo -e "\t\t============================================"
}

# Checks for Kali Linux 2023.4+ or Ubuntu 18.04+
function check_distro() {
    log info "Checking for compatible Linux distribution and version..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_NAME=$ID
        VERSION=$VERSION_ID

        if [[ "$DISTRO_NAME" == "kali" && ( "$VERSION" == "2023.4"|| "$VERSION" == "2024.3" || "$VERSION" == "2024.4" ) ]]; then
            log info "Kali Linux $VERSION detected."
            return 0
        elif [[ "$DISTRO_NAME" == "ubuntu" && ( "$VERSION" == "18.04" || "$VERSION" == "20.04" || "$VERSION" == "22.04" || "$VERSION" > "18.04" ) ]]; then
            log info "Ubuntu $VERSION detected."
            return 0
        else
            log error "Unsupported Linux distribution or version."
            return 1
        fi
    else
        log error "/etc/os-release file not found. Cannot determine Linux distribution."
        return 1
    fi
}


# Project Directory Variables
DEST_DIR="$SCRIPT_DIR/chadv$CHAD_VERSION"

ATTACKTOOL_DIR="$DEST_DIR/attack_tools"

GENAI_DIR="$ATTACKTOOL_DIR/ai_attack_tools"
MEDUSA_DIR="$ATTACKTOOL_DIR/medusa"
MASSCAN_DIR="$ATTACKTOOL_DIR/masscan"

FUZZTOOL_DIR="$DEST_DIR/fuzzing_tools"

AFL_DIR="$FUZZTOOL_DIR/aflnet"
RADAMSA_DIR="$FUZZTOOL_DIR/radamsa"

# Flags
INSTALL=false
SHOULD_REMOVE=false
BUILD=false
NO_SUDO=false

function help() {
    banner
    echo -e "\nThis script installs all necessary dependencies for the chadv1.0 fuzzing workflow.\n"
    echo -e "Usage: $0 [install | build | remove] [--remove | -r] [--dest-dir | -d <dir>] [--no-sudo] [--version | -V] [--help | -h]"
    echo -e "Options:"
    echo -e " -r, --remove\t\tRemove all installed dependencies and files."
    echo -e " -d, --dest-dir\t\tInstallation destination directory (defaults to '$DEST_DIR')."
    echo -e " -n, --no-sudo\t\tRun the script without sudo permissions."
    echo -e " -V, --version\t\tDisplay the version of the install script."
    echo -e " -h, --help\t\tDisplay this help message."
    echo -e "\n"
}

for arg in "$@"; do
    case $arg in
        install)
            INSTALL=true
            ;;
        build)
            BUILD=true
            ;;
        remove | uninstall | -r | --remove)
            SHOULD_REMOVE=true
            ;;
        -d=*|--dest-dir=*)
            DEST_DIR="${arg#*=}"
            shift
            ;;
        --dest-dir)
            DEST_DIR="$2"
            shift
            ;;
        -n|--no-sudo)
            NO_SUDO=true
            ;;
        -V|--version)
            echo "Chadv1.0 install script version: $SCRIPT_VERSION"
            exit 1
            ;;
        -h|--help)
            help
            exit 1
            ;;
        *)
            help
            exit 1
            ;;
    esac
    shift
done

function sanitize_path() {
    local SANITIZED_PATH="$1"
    local SANITIZED_PATH=${SANITIZED_PATH//..\//}
    local SANITIZED_PATH=${SANITIZED_PATH#./}
    local SANITIZED_PATH=${SANITIZED_PATH#/}
    echo "$SANITIZED_PATH"
}

# Root check
if [ "$EUID" -ne 0 ] && [ "$NO_SUDO" = false ]; then
    log error "This script requires root permissions or the '--no-sudo' option."
    # help
    exit 1
fi

# Save output to log file
rm -f /tmp/chad_install.log
LOG_FILE="/tmp/chad_install.log"
exec > >(tee -a $LOG_FILE) 2>&1

command_exists() {
    if ! command -v "$1" &> /dev/null; then
        log error "Command: $1 could not be found! Exiting..."
        exit 1
    fi
}

dir_exists() {
    if [ -d "$1" ]; then
        log info "Directory: $1 already exists."
        return 0
    else
        log info "Directory: $1 not found."
        return 1
    fi
}

function check_repo_connection() {
    local repo_url=$1

    log info "Checking connection to repository: $repo_url"
    if git ls-remote "$repo_url" &> /dev/null; then
        log info "Successfully connected to the repository."
        return 0
    else
        log error "Failed to connect to the repository: $repo_url"
        return 1
    fi
}

function retrieve_file() {
    local file_url=$1
    local destination_path=$2

    log info "Retrieving file from: $file_url"

    # Ensure the parent directory exists
    local destination_dir
    destination_dir=$(dirname "$destination_path")
    if [ ! -d "$destination_dir" ]; then
        log info "Creating directory: $destination_dir"
        mkdir -p "$destination_dir"
    fi

    # Download the file
    command_exists curl
    if curl -o "$destination_path" -L --fail "$file_url"; then
        log info "File successfully retrieved and saved to: $destination_path"
    else
        log error "Failed to retrieve file from: $file_url"
        exit 1
    fi
}

function uninstall() {
    banner
    log info "Removing related files and directories..."
    if [ -d "$DEST_DIR" ]; then
        log info "Removing: $DEST_DIR"
        rm -rf "$DEST_DIR"
    else
        log info "Directory: $DEST_DIR not found."
    fi

    rm -f /bin/radamsa
}

function install_tool() {
    local tool_name=$1
    local repo_url=$2
    local target_dir=$3

    log info "Installing: $tool_name"
    if ! check_repo_connection "$repo_url"; then
        log error "Failed to connect to the repository: $repo_url"
        exit 1
    fi
    if [ ! -d "$target_dir" ]; then
        log info "Cloning repository into: $target_dir"
        if git clone $repo_url "$target_dir"; then
            log info "$tool_name installed successfully."
        else
            log error "Failed to clone $tool_name repository."
            exit 1
        fi
    else
        log info "$tool_name directory already exists."
    fi
}

function install() {
    banner

    if ! check_distro; then
        log error "This script supports only Kali Linux 2023.4 or above and Ubuntu 18.04 or above."
        exit 1
    fi

    echo -e "\n"
    log info "Installing required packages..."
    sudo apt update -y && sudo apt upgrade -y
    sudo apt install -y clang graphviz-dev libcap-dev git make gcc autoconf \
        automake libssl-dev wget curl php-cli wireshark tshark unzip dos2unix 

    log info "Retrieving AI attack tools..."
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/copilot.attack_tool/1_banner_grabber/gc_banner_grabber.c" "$GENAI_DIR/gc_banner_grabber.c"
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/copilot.attack_tool/2_pwd_brute_forcer/gc_brute_force.c" "$GENAI_DIR/gc_brute_force.c"
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/copilot.attack_tool/3_multi_thread_banner_grabber/gc_mt_banner_grabber.c" "$GENAI_DIR/gc_mt_banner_grabber.c"
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/phind.attack_tool/1_banner_grabber/p_banner_grabber.c" "$GENAI_DIR/p_banner_grabber.c"
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/phind.attack_tool/2_pwd_brute_forcer/p_brute_force.c" "$GENAI_DIR/p_brute_force.c"
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/phind.attack_tool/3_multi_thread_banner_grabber/p_mt_banner_grabber.c" "$GENAI_DIR/p_mt_banner_grabber.c"
    retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/gen_ai.attack_tool/Makefile" "$GENAI_DIR/Makefile"

    command_exists git

    # * May need to check to ensure --depth 1 will work
    # Attack Tools 
    install_tool "Medusa" "https://salsa.debian.org/pkg-security-team/medusa" "$MEDUSA_DIR"
    install_tool "Masscan" "https://github.com/robertdavidgraham/masscan" "$MASSCAN_DIR"
    
    # Fuzzing Tools
    install_tool "AFLNet" "https://github.com/aflnet/aflnet.git" "$AFL_DIR"
    install_tool "Radamsa" "https://gitlab.com/akihe/radamsa.git" "$RADAMSA_DIR"

    log info "All tools successfully installed!"
}

# Can't adequately modularize this function since all tools vary in build process
function build() {
    banner
    log info "Building all tools, this may take some time."
    
    # Build AI attack tools
    log info "Building AI attack tools..."
    if [ -d "$GENAI_DIR" ]; then
        cd "$GENAI_DIR"
        if make; then
            log info "AI attack tools built successfully."
        else
            log error "Failed to build AI attack tools."
            exit 1
        fi
        cd "$SCRIPT_DIR"
    else 
        log error "AI attack tools directory not found."
        exit 1
    fi

    # Build Medusa
    # NOTE: Error when building on Ubuntu system, missing openssl libraries
    log info "Building Medusa..."
    if [ -d "$MEDUSA_DIR" ]; then
        cd "$MEDUSA_DIR"
        if ./configure; then
            log info "Medusa successfully configured."
            autoreconf -f -i
            if make; then
                log info "Medusa successfully built."
            else
                log error "Failed to build Medusa."
                log warn "Using the pre-built package for Medusa instead."
                # exit 1
            fi
        else
            log error "Failed to configure Medusa."
            exit 1
        fi
        cd "$SCRIPT_DIR"
    else 
        log error "Medusa directory not found."
        exit 1
    fi
    
    # Build Masscan
    log info "Building Masscan..."
    if [ -d "$MASSCAN_DIR" ]; then
        cd "$MASSCAN_DIR"
        # Get updated Makefile from repository
        command_exists curl
        if [ -f "Makefile" ]; then
            log info "Removing existing Makefile..."
            rm -f Makefile
        fi
        retrieve_file "$REPO_PARENT_URL/$REPO_USER/$REPO_BASE/refs/heads/main/fuzzing/aflnet.masscan/Makefile" "$MASSCAN_DIR/Makefile"
        if make; then
            log info "Masscan built successfully."
        else
            log error "Failed to build Masscan."
            exit 1
        fi
        cd "$SCRIPT_DIR"
    else 
        log error "Masscan directory not found."
        exit 1
    fi

    # Build AFLNet

    # NOTE: AFLnet requires llvm_mode which needs a specific version of
    # clang and llvm; the make command may not work if llvm-config is not found.
    # To fix this issue, LLVM_CONFIG environment variable needs to be set to the 
    # correct path of llvm-config. 

    log info "Building AFLNet..."
    if [ -d "$AFL_DIR" ]; then
        cd "$AFL_DIR"
        # Need to add Distro check here for gmake; x86 won't work on Kali
        if make clean all; then
            log info "AFLnet instrumentation built successfully."
            # May want to add directory check here as well, but should be fine for now
            cd llvm_mode
            if make; then
                log info "llvm_mode built successfully."
            else
                log error "Failed to build llvm_mode."
                log info "Looking for existing llvm-config..."
                # Check for llvm-config-* in /usr/bin
                LLVM_CONFIG=$(ls /usr/bin/llvm-config-* 2>/dev/null | head -n 1)
                if [ -z "$LLVM_CONFIG" ]; then
                    log error "llvm-config version not found in /usr/bin."
                    log info "Checking for LLVM_CONFIG on PATH..."
                    # Check for llvm-config on PATH
                    if [[ ":PATH:" != *":$LLVM_CONFIG:"* ]]; then
                        log error "llvm-config not found on PATH."
                        log error "Please install clang or set LLVM_CONFIG environment variable manually."
                        exit 1
                    else
                        log info "Found llvm-config on PATH."
                    fi
                else 
                    log info "Found llvm-config: $LLVM_CONFIG"
                    export LLVM_CONFIG=$LLVM_CONFIG
                fi

                if make; then
                    log info "llvm_mode built successfully."
                else
                    log error "Could not build llvm_mode with existing llvm-config."
                    exit 1
                fi
            fi
            
            # Move to AFLNet's root directory
            cd ..
            
            if [ -d "in" ]; then
                log info "AFLNet input directory already exists."
            else
                mkdir in out
                log info "Created AFLNet input & output directory."
                echo "masscan -p21-8180 192.168.1.100 --banners --packet-trace --source-mac 08:00:27:6b:b0:67" > in/scan1.txt
                echo "masscan -p80,443 192.168.1.100 --banners" > in/scan2.txt
                echo "masscan -p1-65535 192.168.1.100 --rate=1000" > in/scan3.txt
            fi

            # Move to AFLNet's parent directory
            cd ..
            export AFLNET=$(pwd)/aflnet
            export WORKDIR=$(pwd)
            # export LLVM_CONFIG=$LLVM_CONFIG
            if [[ ":$PATH:" != *":$AFLNET:"* ]]; then
                export PATH=$PATH:$AFLNET
                log info "Added AFLNet to PATH."
            else 
                log info "AFLNet already in PATH."
            fi
            export AFL_PATH=$AFLNET
            log info "AFL_PATH set to: $AFL_PATH"
        else
            log error "Failed to configure AFLNet instrumentation."
            exit 1
        fi 
    else
        log error "AFLNet directory not found."
        exit 1
    fi

    cd "$SCRIPT_DIR"

    # Build Radamsa
    log info "Building Radamsa..."
    if [ -d "$RADAMSA_DIR" ]; then
        cd "$RADAMSA_DIR"
        if make && make install; then
            log info "Radamsa built successfully."
        else
            log error "Failed to build Radamsa."
            exit 1
        fi
        cd "$SCRIPT_DIR"
    else 
        log error "Radamsa directory not found."
        exit 1
    fi
    log info "All tools successfully built!"

    log info "Setting up test environment..."
    # Create www directory for testing with Radamsa

    if [ ! -d "$DEST_DIR/www" ]; then
        mkdir -p "$DEST_DIR/www"
        log info "Created test directory: $DEST_DIR/www"
        echo "<h1> Radamsa Network Fuzzing Test </h1>" > "$DEST_DIR/www/index.html"
        log info "Created web server test file: $DEST_DIR/www/index.html"
        cd "$DEST_DIR"
        # Create a simple web server to serve the test files
        echo "GET / HTTP/1.1" > "$DEST_DIR/http-request.txt"
        echo "Host: localhost:8080" >> "$DEST_DIR/http-request.txt"
        echo "User-Agent: radamsa" >> "$DEST_DIR/http-request.txt"
        echo "Accept: */*" >> "$DEST_DIR/http-request.txt"

        log info "Created HTTP request file: $DEST_DIR/http-request.txt"
    else
        log info "Test directory: $DEST_DIR/www already exists."
    fi
}

if [[ "$INSTALL" = true && "$DEBUG" = false ]]; then
    install
elif [[ "$SHOULD_REMOVE" = true && "$DEBUG" = false ]]; then
    uninstall
elif [[ "$BUILD" = true && "$DEBUG" = false ]]; then
    build
else
    if [ "$DEBUG" = true ]; then
        log warn "Debug mode enabled."
    fi
    help
fi
