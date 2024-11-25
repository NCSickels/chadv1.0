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

# Debug mode flag
DEBUG=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color

# Save output to log file
rm -f /tmp/chad_install.log
LOG_FILE="/tmp/chad_install.log"
exec > >(tee -a $LOG_FILE) 2>&1

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
    echo -e "\t\t============================================"
    echo -e "\t\t     ██████╗██╗  ██╗ █████╗ ██████╗"
    echo -e "\t\t    ██╔════╝██║  ██║██╔══██╗██╔══██╗"
    echo -e "\t\t    ██║     ███████║███████║██║  ██║"
    echo -e "\t\t    ██║     ██╔══██║██╔══██║██║  ██║"
    echo -e "\t\t    ╚██████╗██║  ██║██║  ██║██████╔╝"
    echo -e "\t\t     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝"
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

        if [[ "$DISTRO_NAME" == "kali" && ( "$VERSION" == "2023.4"|| "$VERSION" == "2024.4" ) ]]; then
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

# # Argument parsing
# SHORT=r,d,n,V,h
# LONG=remove,dest-dir,no-sudo,version,help
# VALID_ARGS=$(getopt -a --options $SHORT --longoptions $LONG -- "$@")
# if [[ $? -ne 0 ]]; then
#     exit 1;
# fi

# Project Directory Variables
DEST_DIR="$SCRIPT_DIR/chadv$CHAD_VERSION"

ATTACKTOOL_DIR="$DEST_DIR/attack_tools"

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

# # Check for positional parameters
# if [ "$1" == "install" ]; then
#     INSTALL=true
#     shift
# elif [[ "$1" == "remove" || "$1" == "uninstall" || "$1" == "clean" ]]; then
#     SHOULD_REMOVE=true
#     shift
# elif [ "$1" == "build" ]; then
#     BUILD=true
#     shift
# else
#     help
#     # exit 1
# fi

# # Parse arguments
# eval set -- "$VALID_ARGS"
# while true; do
#     case "$1" in
#         '-r' | '--remove')
#             SHOULD_REMOVE=true
#             ;;
#         '-d' | '--dest-dir')
#             INSTALL_DIR=$2
#             shift
#             ;;
#         '-n'| '--no-sudo')
#             NO_SUDO=true
#             ;;
#         '-V' | '--version')
#             echo "Chadv1.0 install script version: $SCRIPT_VERSION"
#             exit 0
#             ;;
#         '-h' | '--help')
#             help
#             exit 0
#             ;;
#         *)
#             break
#             ;;
#     esac
#     shift
# done

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
        automake libssl-dev wget
    # sudo apt install -y git g++ python3 cmake libhdf5-dev doxygen graphviz make gcc wget \
    #     autoconf automake libssl-dev


    command_exists git

    # Attack Tools 
    install_tool "Medusa" "https://salsa.debian.org/pkg-security-team/medusa" "$MEDUSA_DIR"
    install_tool "Masscan" "https://github.com/robertdavidgraham/masscan" "$MASSCAN_DIR"
    
    # Fuzzing Tools
    install_tool "AFLNet" "https://github.com/aflnet/aflnet.git" "$AFL_DIR"
    install_tool "Radamsa" "https://gitlab.com/akihe/radamsa.git" "$RADAMSA_DIR"
}

# Can't adequately modularize this function since all tools vary in build process
function build() {
    banner
    log info "Building all tools, this may take some time."

    # Build Medusa
    # TODO: Error when building on Ubuntu system, missing openssl libraries
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
                # TODO: Need to set new Medusa path here.
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
                fi

                if make; then
                    log info "llvm_mode built successfully."
                else
                    log error "Could not build llvm_mode with existing llvm-config."
                    exit 1
                fi
            fi
            # Move to AFLNet's parent directory
            cd ../..

            export AFLNET=$(pwd)/aflnet
            export WORKDIR=$(pwd)
            export LLVM_CONFIG=$LLVM_CONFIG

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
