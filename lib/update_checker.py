import requests
import json5 # Use json5 for more robust JSON parsing if needed
import logging
from pathlib import Path
from termcolor import colored
import subprocess
import json # For loading local tools.json

logging.basicConfig(filename='logs/install.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def print_colored_update_checker(text, color, on_color=None, attrs=None):
    """Helper function to print colored text to console from update_checker."""
    print(colored(text, color, on_color, attrs))
    logging.info(f"Console Output ({color}): {text}")

def get_remote_tools_data(remote_url):
    """Fetches the latest tools.json from a remote URL."""
    if not remote_url:
        print_colored_update_checker("[ERROR] Remote tools.json URL is not configured in settings.json.", "red")
        logging.error("Remote tools.json URL is empty.")
        return None

    try:
        print_colored_update_checker(f"\n[*] Fetching latest tool definitions from {remote_url}...", "blue")
        response = requests.get(remote_url, timeout=15) # Increased timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return json5.loads(response.text)
    except requests.exceptions.Timeout:
        logging.error(f"Timeout occurred while fetching remote tools.json from {remote_url}.")
        print_colored_update_checker(f"[ERROR] Request timed out while fetching remote tool data. Check your internet connection.", "red")
        return None
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection error occurred while fetching remote tools.json from {remote_url}.")
        print_colored_update_checker(f"[ERROR] Connection error while fetching remote tool data. Check your internet connection.", "red")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch remote tools.json from {remote_url}: {e}")
        print_colored_update_checker(f"[ERROR] Could not fetch remote tool data: {e}", "red")
        return None
    except json5.JSON5Error as e:
        logging.error(f"Failed to parse remote tools.json: {e}")
        print_colored_update_checker(f"[ERROR] Failed to parse remote tool data: {e}. Remote file might be malformed.", "red")
        return None

def check_for_tool_updates_and_new_tools(local_tools_data, remote_tools_data, installed_tools_names):
    """
    Compares local and remote tool data to find new tools and updates.
    Returns lists of (new_tools, tools_to_update).
    """
    new_tools = []
    tools_to_update = [] # List of (tool_name, tool_data)

    if not remote_tools_data:
        print_colored_update_checker("[WARNING] Remote tool data not available for update check.", "yellow")
        return new_tools, tools_to_update

    remote_flat_tools = {}
    for category_tools in remote_tools_data.values():
        for tool in category_tools:
            remote_flat_tools[tool['name']] = tool

    local_flat_tools = {}
    for category_tools in local_tools_data.values():
        for tool in category_tools:
            local_flat_tools[tool['name']] = tool

    # Check for new tools
    for tool_name, tool_data in remote_flat_tools.items():
        # A tool is "new" if it's in the remote list but not in our local installed directories
        # AND it's not already present in our local tools.json (meaning we haven't seen it before)
        # We also check if it's installable (has github_url and install_path)
        if tool_data.get('github_url') and tool_data.get('install_path') and \
           tool_name not in installed_tools_names and \
           tool_name not in local_flat_tools: # Check if it's genuinely new to our config
            new_tools.append(tool_data)

    # Check for updates to installed tools
    print_colored_update_checker("\n[*] Checking for updates to installed tools (this might take a moment)...", "blue")
    for tool_name in installed_tools_names:
        if tool_name in local_flat_tools: # Ensure it's a tool managed by UHT
            local_tool_data = local_flat_tools[tool_name]
            tool_path_str = local_tool_data.get('install_path')
            repo_url = local_tool_data.get('github_url')

            if tool_path_str and repo_url: # Only check if it's a clonable tool
                tool_path = Path(tool_path_str)

                if tool_path.is_dir() and (tool_path / '.git').is_dir():
                    try:
                        # Fetch latest info from remote
                        subprocess.run(['git', '-C', str(tool_path), 'fetch', '--all'], check=True, capture_output=True)
                        # Compare local branch with remote tracking branch
                        result = subprocess.run(['git', '-C', str(tool_path), 'status', '-uno'], check=True, capture_output=True, text=True)
                        
                        if "Your branch is behind" in result.stdout or "have diverged" in result.stdout:
                            tools_to_update.append(local_tool_data)
                            logging.info(f"Update available for {tool_name}.")
                        # More advanced check: compare local HEAD commit with remote HEAD commit
                        # local_head = subprocess.check_output(['git', '-C', str(tool_path), 'rev-parse', 'HEAD']).strip().decode()
                        # remote_head = subprocess.check_output(['git', '-C', str(tool_path), 'rev-parse', 'origin/main']).strip().decode() # Assuming 'main' branch
                        # if local_head != remote_head:
                        #    tools_to_update.append(local_tool_data)

                    except subprocess.CalledProcessError as e:
                        logging.warning(f"Could not check update for {tool_name} (git error): {e.stderr.strip()}")
                        print_colored_update_checker(f"[WARNING] Could not check update for {tool_name} (Git error). See logs.", "yellow")
                    except Exception as e:
                        logging.warning(f"Unexpected error checking update for {tool_name}: {e}")
                        print_colored_update_checker(f"[WARNING] Unexpected error checking update for {tool_name}. See logs.", "yellow")
                else:
                    logging.info(f"Skipping update check for {tool_name}: not a git repository or install path missing.")
            else:
                logging.info(f"Skipping update check for {tool_name}: no github_url or install_path defined.")

    return new_tools, tools_to_update

def display_update_status(new_tools, tools_to_update):
    """Displays the found new tools and tools with updates."""
    print_colored_update_checker("\n--- Update Status ---", "yellow")

    if new_tools:
        print_colored_update_checker("\nNew Tools Available:", "cyan")
        for tool in new_tools:
            print_colored_update_checker(f"- {tool['name']} ({tool.get('description', 'No description')})", "green")
    else:
        print_colored_update_checker("\nNo new tools found.", "yellow")

    if tools_to_update:
        print_colored_update_checker("\nTools with Available Updates:", "cyan")
        for tool in tools_to_update:
            print_colored_update_checker(f"- {tool['name']}", "green")
    else:
        print_colored_update_checker("\nAll installed tools are up-to-date.", "yellow")

    print_colored_update_checker("\n--- End of Status ---", "yellow")
    # input(colored("\nPress Enter to return to main menu...", 'green')) # Removed input here, handled by main
