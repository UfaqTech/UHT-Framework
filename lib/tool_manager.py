import subprocess
import os
from pathlib import Path
import logging
from termcolor import colored
# Import install_system_package from os_utils for system-level dependencies
from lib.os_utils import install_system_package, install_python_requirements, get_os_type, run_command_in_os_utils

logging.basicConfig(filename='logs/install.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def print_colored_tool_manager(text, color, on_color=None, attrs=None):
    """Helper function to print colored text to console from tool_manager."""
    print(colored(text, color, on_color, attrs))
    logging.info(f"Console Output ({color}): {text}")

def get_installed_tools_names(tools_dir):
    """
    Returns a set of names of currently installed tools based on directory presence
    or specific files for non-git tools.
    """
    installed_names = set()
    if Path(tools_dir).exists():
        for item in Path(tools_dir).iterdir():
            if item.is_dir():
                installed_names.add(item.name)
            elif item.is_file() and item.suffix == '.txt': # For wordlists directly as files
                installed_names.add(item.name)
    return installed_names

def install_tool(tool_data, os_type, tools_base_dir):
    """
    Installs a tool by cloning its GitHub repository and handling dependencies/post-install.
    Handles tools with null github_url/install_path by skipping cloning.
    """
    tool_name = tool_data['name']
    repo_url = tool_data['github_url']
    install_path_str = tool_data['install_path']
    tool_full_path = Path(install_path_str) if install_path_str else None

    print_colored_tool_manager(f"\n[*] Preparing to install {tool_name}...", "blue")
    logging.info(f"Attempting to install {tool_name} from {repo_url} to {tool_full_path}")

    # --- Check and Install System Dependencies ---
    if 'dependencies' in tool_data:
        system_dependencies = tool_data['dependencies'].get(os_type, tool_data['dependencies'].get('default', []))
        
        if system_dependencies:
            print_colored_tool_manager(f"[*] Checking system dependencies for {tool_name} on {os_type}...", "blue")
            for dep in system_dependencies:
                if not install_system_package(dep, os_type):
                    print_colored_tool_manager(f"[ERROR] Failed to install system dependency: {dep}. Aborting installation.", "red")
                    logging.error(f"System dependency {dep} failed for {tool_name}")
                    return False
        else:
            print_colored_tool_manager(f"[INFO] No specific system dependencies defined for {tool_name} on {os_type} (or 'default').", "yellow")
            logging.info(f"No specific system dependencies defined for {tool_name} on {os_type}.")

    # --- Handle GitHub Cloning/Updating ---
    if repo_url and tool_full_path: # Only attempt cloning if both are provided
        tool_full_path.parent.mkdir(parents=True, exist_ok=True) # Ensure parent dir exists

        if tool_full_path.exists():
            print_colored_tool_manager(f"[INFO] {tool_name} directory already exists. Attempting to update...", "yellow")
            logging.info(f"{tool_name} directory exists. Attempting git pull.")
            if not run_command_in_os_utils(['git', '-C', str(tool_full_path), 'pull'], f"Updating {tool_name} repository"):
                print_colored_tool_manager(f"[ERROR] Failed to update {tool_name}.", "red")
                return False
        else:
            print_colored_tool_manager(f"[*] Cloning {tool_name} from {repo_url}...", "blue")
            logging.info(f"Cloning {tool_name} from {repo_url}")
            if not run_command_in_os_utils(['git', 'clone', repo_url, str(tool_full_path)], f"Cloning {tool_name}"):
                print_colored_tool_manager(f"[ERROR] Failed to clone {tool_name}.", "red")
                return False
    elif repo_url and not install_path_str: # Has github_url but no install_path
        print_colored_tool_manager(f"[WARNING] Tool '{tool_name}' has a GitHub URL but no 'install_path'. Skipping cloning. Manual installation might be required.", "yellow")
        logging.warning(f"Tool '{tool_name}' has GitHub URL but no install_path. Skipping cloning.")
    else: # No github_url
        print_colored_tool_manager(f"[INFO] Tool '{tool_name}' does not have a GitHub URL. Skipping cloning. Manual installation might be required.", "yellow")
        logging.info(f"Tool '{tool_name}' has no GitHub URL. Skipping cloning.")


    # --- Run Post-Installation Commands ---
    if 'post_install_commands' in tool_data and tool_data['post_install_commands']:
        # Only run post-install commands if tool_full_path exists (i.e., it was cloned/installed)
        if tool_full_path and tool_full_path.exists():
            print_colored_tool_manager(f"[*] Running post-installation commands for {tool_name}...", "blue")
            logging.info(f"Running post-install commands for {tool_name}")
            for cmd in tool_data['post_install_commands']:
                formatted_cmd = cmd.replace("{{install_path}}", str(tool_full_path))
                
                # Use shell=True for complex commands like those with '&&' or pipes
                # Pass cwd to run command in the tool's directory
                if not run_command_in_os_utils(formatted_cmd, f"Executing post-install command: '{formatted_cmd}'", suppress_error=True, cwd=str(tool_full_path)):
                    print_colored_tool_manager(f"[ERROR] Post-installation command failed: '{formatted_cmd}'. Check command and tool requirements.", "red")
                    logging.error(f"Post-installation command failed for {tool_name}: {formatted_cmd}")
                    return False
        else:
            print_colored_tool_manager(f"[INFO] Skipping post-installation commands for '{tool_name}' as it was not cloned/installed by UHT.", "yellow")
            logging.info(f"Skipping post-install commands for '{tool_name}' as it was not cloned.")

    # Special handling for Python requirements if a requirements.txt exists
    if tool_full_path and tool_full_path.exists() and install_python_requirements(tool_full_path):
        print_colored_tool_manager(f"[+] Python requirements for {tool_name} handled.", "green")
    elif tool_full_path and tool_full_path.exists(): # Only warn if install_path exists but no reqs.txt found
        print_colored_tool_manager(f"[!] Could not handle Python requirements for {tool_name} (if any).", "yellow")
        logging.warning(f"Could not handle Python requirements for {tool_name}.")


    print_colored_tool_manager(f"\n[SUCCESS] {tool_name} installation/update completed.", "green")
    return True

def run_tool(tool_data, tools_base_dir): # tools_base_dir is not used but kept for consistency
    """
    Runs an installed tool.
    Handles tools with null install_path (web resources, manual installs) by displaying info.
    """
    tool_name = tool_data['name']
    
    # Handle run_command being a string or an OS-specific dictionary
    run_command_raw = tool_data['run_command']
    current_os_type = get_os_type() # Get current OS type
    
    if isinstance(run_command_raw, dict):
        run_command = run_command_raw.get(current_os_type, run_command_raw.get('default'))
        if run_command is None:
            print_colored_tool_manager(f"[ERROR] No run command defined for {tool_name} on OS '{current_os_type}' or 'default'.", "red")
            logging.error(f"No run command for {tool_name} on {current_os_type}.")
            return False
    else:
        run_command = run_command_raw # It's a simple string command

    tool_full_path = Path(tool_data['install_path']) if tool_data['install_path'] else None

    # For tools with null install_path (web resources, manual installs), we just display info
    if not tool_full_path:
        print_colored_tool_manager(f"\n[INFO] {tool_name} is a web resource or requires manual setup. Cannot run directly via UHT.", "yellow")
        print_colored_tool_manager(f"Description: {tool_data.get('description', 'No description provided.')}", "cyan")
        print_colored_tool_manager(f"Run Command/Access: {run_command}", "cyan")
        input(colored("\nPress Enter to return...", 'green'))
        return True # Consider it "run" successfully as it displayed info

    if not tool_full_path.exists():
        print_colored_tool_manager(f"[ERROR] {tool_name} is not installed (directory not found). Please install it first.", "red")
        return False

    print_colored_tool_manager(f"\n[*] Running {tool_name}...", "blue")
    logging.info(f"Running {tool_name} with command: {run_command} from {tool_full_path}")

    try:
        # Use run_command_in_os_utils for consistency
        # Pass cwd if tool_full_path is available
        cmd_cwd = str(tool_full_path) if tool_full_path else None
        
        if not run_command_in_os_utils(run_command, f"Running {tool_name}", suppress_error=False, cwd=cmd_cwd):
            print_colored_tool_manager(f"[ERROR] {tool_name} exited with an error. Check tool output above.", "red")
            return False
        print_colored_tool_manager(f"\n[SUCCESS] {tool_name} finished execution.", "green")
        return True
    except Exception as e:
        print_colored_tool_manager(f"[ERROR] An unexpected error occurred while running {tool_name}: {e}", "red")
        logging.error(f"Unexpected error running {tool_name}: {e}")
    return False

