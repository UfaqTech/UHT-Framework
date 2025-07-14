#!/bin/bash

# UHT (Ufaq Hacking Toolkit) Installer
# Created by Awais Nawaz (UfaqTech)

# --- Colors for Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Logging Function ---
log_file="logs/install.log"
mkdir -p logs/ # Ensure logs directory exists
exec > >(tee -a "$log_file") 2>&1 # Redirect stdout and stderr to both console and log file

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UHT (Ufaq Hacking Toolkit) Installer  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Starting installation at $(date)${NC}"

# --- Check for Root/Sudo (Optional but recommended for system-wide installs) ---
if [[ "$EUID" -ne 0 ]]; then
    echo -e "${YELLOW}[INFO] Running without root privileges. Some installations might require sudo.${NC}"
    echo -e "${YELLOW}You might be prompted for your password for system-wide package installations.${NC}"
fi

# --- OS Detection ---
OS_TYPE=""
if [ -d "/data/data/com.termux/files" ]; then
    OS_TYPE="Termux"
    echo -e "${GREEN}[+] Detected OS: Termux${NC}"
elif [ -f "/etc/os-release" ]; then
    . /etc/os-release
    if [[ "$ID" == "debian" || "$ID_LIKE" == "debian" || "$ID" == "ubuntu" ]]; then
        OS_TYPE="Debian_Based_Linux"
        echo -e "${GREEN}[+] Detected OS: Debian/Ubuntu-based Linux${NC}"
    elif [[ "$ID" == "arch" || "$ID_LIKE" == "arch" ]]; then
        OS_TYPE="Arch_Based_Linux"
        echo -e "${GREEN}[+] Detected OS: Arch-based Linux${NC}"
    else
        OS_TYPE="Other_Linux"
        echo -e "${YELLOW}[!] Detected OS: Other Linux distribution. Package management might differ.${NC}"
    fi
elif [[ "$(uname)" == "Darwin" ]]; then
    OS_TYPE="macOS"
    echo -e "${GREEN}[+] Detected OS: macOS${NC}"
elif [[ "$(uname)" == "Linux" ]]; then # Generic Linux if os-release not found
    OS_TYPE="Linux"
    echo -e "${GREEN}[+] Detected OS: Generic Linux${NC}"
elif [[ "$(expr substr $(uname -s) 1 5)" == "MINGW" || "$(expr substr $(uname -s) 1 5)" == "MSYS_" || "$(expr substr $(uname -s) 1 5)" == "CYGWIN" ]]; then
    OS_TYPE="Windows"
    echo -e "${GREEN}[+] Detected OS: Windows (Git Bash/Cygwin/MSYS2)${NC}"
else
    echo -e "${RED}[ERROR] Could not determine OS type. Exiting.${NC}"
    exit 1
fi

# --- Function to Install System Packages ---
install_system_package() {
    package_name=$1
    echo -e "${BLUE}[*] Checking for system package: $package_name...${NC}"
    if ! command -v "$package_name" &> /dev/null; then
        echo -e "${YELLOW}[!] $package_name not found. Attempting to install...${NC}"
        case "$OS_TYPE" in
            "Termux")
                pkg update -y && pkg install -y "$package_name"
                ;;
            "Debian_Based_Linux"|"Linux") # Generic Linux also uses apt if available
                sudo apt update -y && sudo apt install -y "$package_name"
                ;;
            "Arch_Based_Linux")
                sudo pacman -Sy --noconfirm "$package_name"
                ;;
            "macOS")
                if ! command -v brew &> /dev/null; then
                    echo -e "${YELLOW}[!] Homebrew not found. Installing Homebrew...${NC}"
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    if [ $? -ne 0 ]; then
                        echo -e "${RED}[ERROR] Failed to install Homebrew. Please install it manually.${NC}"
                        return 1
                    fi
                fi
                brew install "$package_name"
                ;;
            "Windows")
                if ! command -v choco &> /dev/null; then
                    echo -e "${YELLOW}[!] Chocolatey not found. Please install Chocolatey manually (https://chocolatey.org/install) or install dependencies manually.${NC}"
                    return 1
                fi
                choco install -y "$package_name"
                ;;
            *)
                echo -e "${RED}[ERROR] Automatic installation for $package_name not supported on this OS.${NC}"
                return 1
                ;;
        esac
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[+] $package_name installed successfully.${NC}"
        else
            echo -e "${RED}[ERROR] Failed to install $package_name. Please install it manually.${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}[+] $package_name is already installed.${NC}"
    fi
    return 0
}

# --- Install Core System Dependencies ---
echo -e "${BLUE}\n[*] Installing core system dependencies...${NC}"
install_system_package "git" || exit 1

# Handle Python and Pip installation based on OS type
if [[ "$OS_TYPE" == "Termux" ]]; then
    install_system_package "python" || exit 1
    install_system_package "python-pip" || exit 1
elif [[ "$OS_TYPE" == "Windows" ]]; then
    # On Windows, python and pip are often installed via official installer or choco
    install_system_package "python" || install_system_package "python3" || exit 1
    install_system_package "pip" || install_system_package "pip3" || exit 1
else # For Debian/Ubuntu-based, Arch-based, macOS, and Generic Linux
    install_system_package "python3" || exit 1
    install_system_package "python3-pip" || install_system_package "python-pip" || exit 1 # Fallback for pip
fi

# --- Create Essential Directories ---
echo -e "${BLUE}\n[*] Creating essential directories...${NC}"
mkdir -p config/ tools/ logs/ docs/
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Essential directories created.${NC}"
else
    echo -e "${RED}[ERROR] Failed to create directories.${NC}"
    exit 1
fi

# --- Create Placeholder Files (if not exist) ---
echo -e "${BLUE}\n[*] Creating placeholder files if missing...${NC}"
touch tools/.keep # Ensure tools directory is tracked by git
if [ ! -f "config/tools.json" ]; then
    echo '{}' > config/tools.json
    echo -e "${YELLOW}[!] Created empty config/tools.json. Please populate it with tool data.${NC}"
fi
if [ ! -f "config/settings.json" ]; then
    echo '{"UHT_VERSION": "1.0.0", "TOOLS_DIR": "tools", "REMOTE_TOOLS_JSON_URL": ""}' > config/settings.json
    echo -e "${GREEN}[+] Created default config/settings.json.${NC}"
fi
if [ ! -f "requirements.txt" ]; then
    echo "json5" > requirements.txt # Minimal initial requirement
    echo "termcolor" >> requirements.txt # For colored output in Python
    echo "requests" >> requirements.txt # For update_checker (fetching remote JSON)
    echo -e "${YELLOW}[!] Created basic requirements.txt. Please add more Python dependencies as needed.${NC}"
fi

# --- Setup Python Virtual Environment (Recommended) ---
echo -e "${BLUE}\n[*] Setting up Python virtual environment...${NC}"
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python not found. Virtual environment setup failed.${NC}"
    exit 1
fi

if [ -d "venv" ]; then
    echo -e "${YELLOW}[INFO] Virtual environment 'venv' already exists. Skipping creation.${NC}"
else
    "$PYTHON_CMD" -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[+] Virtual environment 'venv' created.${NC}"
    else
        echo -e "${RED}[ERROR] Failed to create virtual environment. Please check your Python installation.${NC}"
        exit 1
    fi
fi

# Activate virtual environment and install requirements
echo -e "${BLUE}\n[*] Activating virtual environment and installing Python dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Python dependencies installed successfully.${NC}"
else
    echo -e "${RED}[ERROR] Failed to install Python dependencies. Please check 'requirements.txt'.${NC}"
    deactivate # Deactivate venv on error
    exit 1
fi
deactivate # Deactivate after installation

echo -e "${GREEN}\n========================================${NC}"
echo -e "${GREEN}  UHT Installation Complete!            ${NC}"
echo -e "${GREEN}  To run UHT: source venv/bin/activate  ${NC}"
echo -e "${GREEN}              python uht.py             ${NC}"
echo -e "${GREEN}========================================${NC}"

exit 0

