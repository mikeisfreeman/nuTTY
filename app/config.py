import json
import os
from cryptography.fernet import Fernet
import appdirs
import shutil


# Define the application name
APP_NAME = "nuTTY"

# Get the user's config directory
CONFIG_DIR = appdirs.user_config_dir(APP_NAME)

# Ensure the config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Define file paths
KEY_FILE = os.path.join(CONFIG_DIR, 'nuTTY_key')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
CONNECTIONS_FILE = os.path.join(CONFIG_DIR, 'connections.dat')

def load_or_generate_key():
    """Load the secret key from a file or generate a new one if it doesn't exist."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        # Set appropriate permissions for the key file
        os.chmod(KEY_FILE, 0o600)
        return key
    
def load_config():
    """Load configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Helper function to get connections file path
def get_connections_file_path():
    return CONNECTIONS_FILE


def find_terminals(self):
    # List of common terminal emulators with their names and commands
    common_terminal_names = {
        "XTerm": ("xterm", "xterm -hold -e {ssh_command}"),
        "GNOME Terminal": ("gnome-terminal", "gnome-terminal -- bash -c '{ssh_command}; exec bash'"),
        "Konsole": ("konsole", "konsole -e bash -c '{ssh_command}; exec bash'"),
        "XFCE Terminal": ("xfce4-terminal", "xfce4-terminal --hold -e '{ssh_command}'"),
        "LXTerminal": ("lxterminal", "lxterminal -e bash -c '{ssh_command}; exec bash'"),
        "Tilix": ("tilix", "tilix -e bash -c '{ssh_command}; exec bash'"),
        "Alacritty": ("alacritty", "alacritty -e bash -c '{ssh_command}; exec bash'"),
        "Kitty": ("kitty", "kitty bash -c '{ssh_command}; exec bash'"),
        "URxvt": ("urxvt", "urxvt -hold -e {ssh_command}"),
        "st": ("st", "st -e bash -c '{ssh_command}; exec bash'"),
        "Eterm": ("eterm", "eterm -e bash -c '{ssh_command}; exec bash'"),
        "Mate Terminal": ("mate-terminal", "mate-terminal -e bash -c '{ssh_command}; exec bash'")
    }

    available_terminal_emulators = {}

    # Check if the terminal emulator command is available in the system PATH
    for name, (command, _) in common_terminal_names.items():
        if shutil.which(command):  # Check if the terminal command is available
            available_terminal_emulators[name] = (command, common_terminal_names[name][1])  # Add to available terminals
    return available_terminal_emulators