import json
import logging
import sys
from pathlib import Path
from termcolor import colored
import os
import subprocess

# Import UHT modules
from lib.os_utils import get_os_type, install_system_package # install_system_package is now in os_utils
from lib.menu_handler import (
    clear_screen, display_banner, display_main_menu,
    display_tool_menu, display_tool_options, confirm_action
)
from lib.tool_manager import install_tool, run_tool, get_installed_tools_names
from lib.update_checker import get_remote_tools_data, check_for_tool_updates_and_new_tools, display_update_status


# --- Setup Logging ---
log_file_path = Path('logs/uht.log')
log_file_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=str(log_file_path), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global Variables ---
UHT_VERSION = "Unknown"
TOOLS_DIR = "tools"
REMOTE_TOOLS_JSON_URL = ""
TOOLS_DATA = {}
OS_TYPE = get_os_type() # Get OS type once at startup

# --- Load Configuration ---
def load_config():
    """Loads settings and tools data from JSON files."""
    global UHT_VERSION, TOOLS_DIR, REMOTE_TOOLS_JSON_URL, TOOLS_DATA

    settings_path = Path('config/settings.json')
    tools_path = Path('config/tools.json')

    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            UHT_VERSION = settings.get("UHT_VERSION", "Unknown")
            TOOLS_DIR = settings.get("TOOLS_DIR", "tools")
            REMOTE_TOOLS_JSON_URL = settings.get("REMOTE_TOOLS_JSON_URL", "")
    except FileNotFoundError:
        logging.error(f"Settings file not found: {settings_path}")
        print(colored(f"[ERROR] Settings file not found: {settings_path}. Run install.sh.", 'red'))
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing settings.json: {e}")
        print(colored(f"[ERROR] Error parsing settings.json: {e}. Check file format.", 'red'))
        sys.exit(1)

    try:
        with open(tools_path, 'r') as f:
            TOOLS_DATA = json.load(f)
    except FileNotFoundError:
        logging.error(f"Tools data file not found: {tools_path}")
        print(colored(f"[ERROR] Tools data file not found: {tools_path}. Run install.sh.", 'red'))
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing tools.json: {e}")
        print(colored(f"[ERROR] Error parsing tools.json: {e}. Check file format.", 'red'))
        sys.exit(1)

def self_update_uht():
    """Updates the UHT framework itself via git pull."""
    print(colored("\n[*] Updating UHT Framework...", 'blue'))
    logging.info("Starting UHT self-update.")
    try:
        subprocess.run(['git', 'pull'], check=True, cwd=Path(__file__).parent)
        print(colored("[+] UHT Framework updated successfully!", 'green'))
        logging.info("UHT Framework updated successfully.")
        load_config() # Reload config to get new version if updated
    except subprocess.CalledProcessError as e:
        print(colored(f"[ERROR] Failed to update UHT Framework: {e}", 'red'))
        logging.error(f"Failed to update UHT Framework: {e}")
    except Exception as e:
        print(colored(f"[ERROR] An unexpected error occurred during UHT update: {e}", 'red'))
        logging.error(f"Unexpected error during UHT update: {e}")
    input(colored("\nPress Enter to continue...", 'green'))


def main():
    """Main function to run the UHT CLI."""
    load_config()

    while True:
        display_banner(UHT_VERSION)
        categories = list(TOOLS_DATA.keys())
        main_menu_choice = display_main_menu(categories)

        if main_menu_choice == "0":
            print(colored("\nExiting UHT. Goodbye!", 'red'))
            break
        elif main_menu_choice.isdigit() and 1 <= int(main_menu_choice) <= len(categories):
            selected_category_index = int(main_menu_choice) - 1
            selected_category_name = categories[selected_category_index]
            category_tools = TOOLS_DATA[selected_category_name]
            
            # Refined filtering logic for tool compatibility
            final_compatible_tools = []
            for tool in category_tools:
                os_compat_list = tool.get('os_compat', [])
                skip_if_not_supported = tool.get('skip_if_os_not_supported', False)

                is_compatible = False
                if OS_TYPE in os_compat_list:
                    is_compatible = True
                elif "any" in os_compat_list: # Explicitly handle "any" OS compatibility
                    is_compatible = True
                elif not os_compat_list and not skip_if_not_supported:
                    # If os_compat_list is empty, treat as universally compatible (unless explicitly skipped)
                    # This case handles tools that don't specify os_compat but are not skipped.
                    is_compatible = True
                
                # If tool explicitly says to skip on unsupported OS, and it's not compatible, then skip.
                if skip_if_not_supported and not is_compatible:
                    continue # Skip this tool

                if is_compatible:
                    final_compatible_tools.append(tool)

            installed_tools_names = get_installed_tools_names(TOOLS_DIR)

            while True:
                tool_menu_choice = display_tool_menu(selected_category_name, final_compatible_tools, installed_tools_names)

                if tool_menu_choice == "B" or tool_menu_choice == "b":
                    break
                elif tool_menu_choice == "0":
                    print(colored("\nExiting UHT. Goodbye!", 'red'))
                    sys.exit(0)
                elif tool_menu_choice.isdigit() and 1 <= int(tool_menu_choice) <= len(final_compatible_tools):
                    selected_tool_index = int(tool_menu_choice) - 1
                    selected_tool_data = final_compatible_tools[selected_tool_index]

                    while True:
                        tool_options_choice = display_tool_options(selected_tool_data['name'])

                        if tool_options_choice == "B" or tool_options_choice == "b":
                            break
                        elif tool_options_choice == "0":
                            print(colored("\nExiting UHT. Goodbye!", 'red'))
                            sys.exit(0)
                        elif tool_options_choice == "1": # Install/Update
                            install_tool(selected_tool_data, OS_TYPE, TOOLS_DIR)
                            installed_tools_names = get_installed_tools_names(TOOLS_DIR) # Refresh installed status
                            input(colored("\nPress Enter to continue...", 'green'))
                        elif tool_options_choice == "2": # Run
                            # For tools with null install_path (manual/web-based), just display info
                            if not selected_tool_data['install_path'] and not selected_tool_data['github_url']:
                                run_tool(selected_tool_data, TOOLS_DIR) # This will just display info
                                # run_tool already handles input, no need for extra input() here
                                continue

                            # Check if the tool is actually installed before running
                            # Note: get_installed_tools_names checks directory existence.
                            # For tools that are just binaries or single files, this might need refinement
                            # if they don't create a dedicated folder.
                            if selected_tool_data['name'] not in get_installed_tools_names(TOOLS_DIR):
                                print(colored(f"[!] {selected_tool_data['name']} is not installed. Please install it first.", 'yellow'))
                                if confirm_action("Do you want to install it now?"):
                                    install_tool(selected_tool_data, OS_TYPE, TOOLS_DIR)
                                    installed_tools_names = get_installed_tools_names(TOOLS_DIR) # Refresh
                                    if selected_tool_data['name'] not in installed_tools_names: # Re-check if installation was successful
                                        input(colored("\nInstallation failed. Press Enter to continue...", 'red'))
                                        continue # Go back to tool options
                                else:
                                    input(colored("\nPress Enter to continue...", 'green'))
                                    continue # Go back to tool options

                            # Now run the tool if it's installed
                            if selected_tool_data['name'] in installed_tools_names:
                                run_tool(selected_tool_data, TOOLS_DIR)
                            input(colored("\nPress Enter to continue...", 'green'))
                        else:
                            print(colored("Invalid choice. Please try again.", 'red'))
                            input(colored("\nPress Enter to continue...", 'green'))
                else:
                    print(colored("Invalid choice. Please try again.", 'red'))
                    input(colored("\nPress Enter to continue...", 'green'))
        elif main_menu_choice == str(len(categories) + 1): # Check for Updates / New Tools
            clear_screen()
            remote_data = get_remote_tools_data(REMOTE_TOOLS_JSON_URL)
            if remote_data:
                installed_names = get_installed_tools_names(TOOLS_DIR)
                new_tools, tools_to_update = check_for_tool_updates_and_new_tools(TOOLS_DATA, remote_data, installed_names)
                display_update_status(new_tools, tools_to_update)
            else:
                print(colored("\n[ERROR] Could not perform update check. See logs for details.", 'red'))
            input(colored("\nPress Enter to continue...", 'green')) # Added input here
            
        elif main_menu_choice == str(len(categories) + 2): # Update UHT Framework (Self-Update)
            # Ensure git is installed before attempting self-update
            if not install_system_package("git", OS_TYPE):
                print(colored("\n[ERROR] Git is required for UHT self-update. Please install it manually.", "red"))
                input(colored("\nPress Enter to continue...", 'green'))
            else:
                self_update_uht()
        else:
            print(colored("Invalid choice. Please try again.", 'red'))
            input(colored("\nPress Enter to continue...", 'green'))

if __name__ == "__main__":
    # Ensure virtual environment is active before running main
    if 'VIRTUAL_ENV' not in os.environ:
        print(colored("[!] Virtual environment not active.", 'yellow'))
        print(colored("Please activate the virtual environment using:", 'yellow'))
        print(colored("    source venv/bin/activate", 'cyan'))
        print(colored("Then run: python uht.py", 'cyan'))
        sys.exit(1)
        
    main()

