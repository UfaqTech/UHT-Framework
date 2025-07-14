# lib/os_utils.py
import platform
import subprocess
import os
from pathlib import Path
import logging
from termcolor import colored

logging.basicConfig(filename='logs/install.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def print_colored_os_utils(text, color, on_color=None, attrs=None):
    """Helper function to print colored text to console from os_utils."""
    print(colored(text, color, on_color, attrs))
    logging.info(f"Console Output ({color}): {text}")

def run_command_in_os_utils(command, description, check_output=False, suppress_error=False, cwd=None):
    """
    Runs a shell command and logs its output.
    Returns True on success, False on failure.
    This version uses shell=True for broader command compatibility.
    """
    cmd_str = command if isinstance(command, str) else ' '.join(command)
    print_colored_os_utils(f"[*] {description}...", "blue")
    logging.info(f"Executing command: {cmd_str}")
    try:
        result = subprocess.run(cmd_str, shell=True, check=True, capture_output=True, text=True, encoding='utf-8', cwd=cwd)
        logging.info(f"Command '{cmd_str}' stdout:\n{result.stdout.strip()}")
        if result.stderr:
            logging.warning(f"Command '{cmd_str}' stderr:\n{result.stderr.strip()}")
        print_colored_os_utils(f"[+] {description} completed successfully.", "green")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{cmd_str}' failed with exit code {e.returncode}. stderr:\n{e.stderr.strip()}")
        if not suppress_error:
            print_colored_os_utils(f"[ERROR] {description} failed: {e.stderr.strip()}", "red")
        return False
    except FileNotFoundError:
        print_colored_os_utils(f"[ERROR] Command '{command[0] if isinstance(command, list) else command.split()[0]}' not found. Is it in PATH?", "red")
        logging.error(f"Command '{command[0] if isinstance(command, list) else command.split()[0]}' not found.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during '{cmd_str}': {e}")
        if not suppress_error:
            print_colored_os_utils(f"[ERROR] An unexpected error occurred during {description}: {e}", "red")
        return False

def get_os_type():
    """Detects the operating system type."""
    system = platform.system()
    if 'ANDROID_ROOT' in os.environ or Path('/data/data/com.termux/files').is_dir():
        print_colored_os_utils("[+] Detected OS: Termux", "green")
        logging.info("Detected OS: Termux")
        return "termux"
    elif system == "Linux":
        if Path("/etc/os-release").exists():
            with open("/etc/os-release", "r") as f:
                content = f.read()
                if "ID=debian" in content or "ID_LIKE=debian" in content or "ID=ubuntu" in content:
                    print_colored_os_utils("[+] Detected OS: Debian/Ubuntu-based Linux", "green")
                    logging.info("Detected OS: Debian_Based_Linux")
                    return "debian_based_linux"
                elif "ID=arch" in content or "ID_LIKE=arch" in content:
                    print_colored_os_utils("[+] Detected OS: Arch-based Linux", "green")
                    logging.info("Detected OS: Arch_Based_Linux")
                    return "arch_based_linux"
            print_colored_os_utils("[!] Detected OS: Other Linux distribution. Package management might differ.", "yellow")
            logging.info("Detected OS: Other_Linux (Fallback)")
            return "linux" # Generic Linux for other distros
        print_colored_os_utils("[!] Detected OS: Generic Linux (No os-release found).", "yellow")
        logging.info("Detected OS: Generic_Linux (No os-release)")
        return "linux"
    elif system == "Windows":
        print_colored_os_utils("[+] Detected OS: Windows", "green")
        logging.info("Detected OS: Windows")
        return "windows"
    elif system == "Darwin": # macOS
        print_colored_os_utils("[+] Detected OS: macOS", "green")
        logging.info("Detected OS: macos")
        return "macos"
    print_colored_os_utils(f"[ERROR] Unsupported OS detected: {system}. Exiting.", "red")
    logging.critical(f"Unsupported OS detected: {system}")
    return "unsupported" # Return unsupported instead of exiting, let main handle

def check_command_exists(command_name):
    """Checks if a command exists in the system's PATH."""
    try:
        subprocess.run(['which', command_name], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_system_package(package_name, os_type):
    """
    Checks if a system package is installed and attempts to install/update it.
    Returns True if package is available/installed, False otherwise.
    """
    print_colored_os_utils(f"[*] Checking for system package: {package_name}", "blue")
    logging.info(f"Checking for system package: {package_name} on {os_type}")

    if package_name.strip() == "":
        return True # Empty dependency is always "met"

    # Special check for python/python3 as they might be installed but 'which python' might point to venv
    if package_name in ["python", "python3", "pip", "pip3", "go", "java", "perl", "ruby", "bash", "powershell"]:
        if check_command_exists(package_name):
            print_colored_os_utils(f"[+] {package_name} is already installed.", "green")
            return True
        # For Java, check for common java executables
        if package_name == "java":
            if check_command_exists("java") or check_command_exists("javac"):
                print_colored_os_utils(f"[+] Java (or JDK) is already installed.", "green")
                return True
    else: # For other commands, just check if the command itself exists
        if check_command_exists(package_name):
            print_colored_os_utils(f"[+] {package_name} is already installed.", "green")
            return True

    print_colored_os_utils(f"[!] {package_name} not found. Attempting to install...", "yellow")
    install_cmd = []
    update_cmd = []

    if os_type == "termux":
        update_cmd = ['pkg', 'update', '-y']
        install_cmd = ['pkg', 'install', '-y', package_name]
    elif os_type == "debian_based_linux":
        update_cmd = ['sudo', 'apt', 'update', '-y']
        install_cmd = ['sudo', 'apt', 'install', '-y', package_name]
    elif os_type == "arch_based_linux":
        update_cmd = ['sudo', 'pacman', '-Sy', '--noconfirm']
        install_cmd = ['sudo', 'pacman', '-S', '--noconfirm', package_name]
    elif os_type == "windows":
        # For Windows, we assume Chocolatey or Winget.
        # Note: Winget needs exact IDs. This is a best-effort attempt.
        if check_command_exists("choco"):
            install_cmd = ['choco', 'install', '-y', package_name]
        elif check_command_exists("winget"):
            # This is a simplification. Winget often needs --id and specific package IDs.
            # E.g., 'winget install --id Git.Git' not 'winget install git'
            # For most common tools, the name might work.
            install_cmd = ['winget', 'install', '-e', '--id', package_name] # -e for exact match
            print_colored_os_utils("[WARNING] Winget might require exact package IDs. If installation fails, try manual install.", "yellow")
        else:
            print_colored_os_utils("[ERROR] Neither Chocolatey nor Winget found. Please install them or install dependencies manually on Windows.", "red")
            logging.error("No package manager found for Windows.")
            return False
    elif os_type == "macos":
        # For macOS, we assume Homebrew
        if check_command_exists("brew"):
            update_cmd = ['brew', 'update']
            install_cmd = ['brew', 'install', package_name]
        else:
            print_colored_os_utils("[ERROR] Homebrew not found. Please install Homebrew or install dependencies manually on macOS.", "red")
            logging.error("Homebrew not found for macOS.")
            return False
    else: # Generic Linux or unsupported
        print_colored_os_utils(f"[ERROR] Automatic installation for '{package_name}' not supported on this OS type ('{os_type}'). Please install manually.", "red")
        logging.error(f"Cannot auto-install '{package_name}' on generic/unsupported OS.")
        return False

    # First, run update command for the package manager (if applicable)
    if update_cmd:
        if not run_command_in_os_utils(update_cmd, f"Updating package list for {os_type}", suppress_error=True):
            print_colored_os_utils(f"[WARNING] Failed to update package list for {os_type}. Trying to install {package_name} anyway.", "yellow")
            logging.warning(f"Failed to update package list for {os_type}.")

    # Then, run install command
    if install_cmd:
        if run_command_in_os_utils(install_cmd, f"Installing {package_name}"):
            return True
    return False

def install_python_requirements(tool_path):
    """Installs Python requirements from a requirements.txt file within a tool's directory."""
    req_file = Path(tool_path) / "requirements.txt"
    if req_file.exists():
        print_colored_os_utils(f"[*] Installing Python requirements for {tool_path}...", "blue")
        logging.info(f"Installing Python requirements for {tool_path}")
        
        # Use 'pip3' if available, otherwise 'pip'
        pip_cmd_base = ['pip3']
        if not check_command_exists('pip3'):
            pip_cmd_base = ['pip']
            if not check_command_exists('pip'):
                print_colored_os_utils("[ERROR] Neither 'pip3' nor 'pip' found. Cannot install Python requirements.", "red")
                logging.error("Neither 'pip3' nor 'pip' found for Python requirements.")
                return False

        pip_cmd = pip_cmd_base + ['install', '-r', str(req_file)]
        
        if run_command_in_os_utils(pip_cmd, f"Installing Python packages for {tool_path}"):
            return True
    else:
        print_colored_os_utils(f"[INFO] No requirements.txt found for {tool_path}.", "yellow")
        logging.info(f"No requirements.txt found for {tool_path}.")
    return False

