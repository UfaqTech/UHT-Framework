import os
from termcolor import colored

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner(uht_version):
    """Displays the UHT banner and version."""
    clear_screen()
    banner = f"""
██╗   ██╗██╗  ██╗████████╗
██║   ██║██║  ██║╚══██╔══╝
██║   ██║███████║   ██║
██║   ██║██╔══██║   ██║
╚██████╔╝██║  ██║   ██║
 ╚═════╝ ╚═╝  ╚═╝   ╚═╝    {colored('Ufaq Hacking Toolkit', 'cyan')}
                          (UHT) {colored(f'v{uht_version}', 'green')}

{colored('Created by Awais Nawaz (UfaqTech)', 'magenta')}
    """
    print(banner)

def display_main_menu(categories):
    """Displays the main category menu."""
    print(colored("\nSelect a Category:", 'yellow'))
    for i, category in enumerate(categories):
        print(f"[{i + 1}] {colored(category, 'cyan')}")

    # Add fixed options at the end
    fixed_options_start_index = len(categories) + 1
    print(colored(f"[{fixed_options_start_index}] Check for Updates / New Tools", 'blue'))
    print(colored(f"[{fixed_options_start_index + 1}] Update UHT Framework (Self-Update)", 'blue'))
    print(colored("[0] Exit", 'red'))
    
    try:
        choice = input(colored("\nEnter your choice: ", 'green')).strip()
        return choice
    except KeyboardInterrupt:
        print(colored("\nExiting UHT. Goodbye!", 'red'))
        return "0"

def display_tool_menu(category_name, tools_list, installed_tools_names):
    """Displays tools within a chosen category."""
    clear_screen()
    print(colored(f"UHT > {category_name} Tools\n", 'yellow'))

    if not tools_list:
        print(colored(f"No compatible tools found in '{category_name}' category for your OS yet.", 'red'))
        input(colored("\nPress Enter to go back...", 'green'))
        return None

    for i, tool in enumerate(tools_list):
        status = colored("(Not Installed)", 'red')
        if tool['install_path'] and Path(tool['install_path']).exists(): # Check if install_path exists
            status = colored("(Installed)", 'green')
        elif not tool['github_url'] and not tool['install_path']: # For web resources/manual tools
             status = colored("(External/Manual)", 'yellow')
        
        print(f"[{i + 1}] {colored(tool['name'], 'cyan')} {status}")

    print(colored("[B] Back to Main Menu", 'blue'))
    print(colored("[0] Exit", 'red'))

    try:
        choice = input(colored("\nEnter your choice: ", 'green')).strip()
        return choice
    except KeyboardInterrupt:
        print(colored("\nExiting UHT. Goodbye!", 'red'))
        return "0"

def display_tool_options(tool_name):
    """Displays options for a specific tool."""
    clear_screen()
    print(colored(f"UHT > {tool_name}\n", 'yellow'))
    print(colored("[1] Install/Update Tool", 'cyan'))
    print(colored("[2] Run Tool", 'green'))
    print(colored("[B] Back to Category", 'blue'))
    print(colored("[0] Exit", 'red'))

    try:
        choice = input(colored("\nEnter your choice: ", 'green')).strip()
        return choice
    except KeyboardInterrupt:
        print(colored("\nExiting UHT. Goodbye!", 'red'))
        return "0"

def confirm_action(prompt):
    """Asks for user confirmation."""
    while True:
        response = input(colored(f"{prompt} (y/n): ", 'yellow')).strip().lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print(colored("Invalid input. Please enter 'y' or 'n'.", 'red'))
