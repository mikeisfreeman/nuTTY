import json
import os
from cryptography.fernet import Fernet
import appdirs
import shutil
import keyring

# Define the application name
APP_NAME = "nuTTY"
KEY_ID = "encryption_key"

# Get the user's config directory
CONFIG_DIR = appdirs.user_config_dir(APP_NAME)

# Ensure the config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Define file paths
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
CONNECTIONS_FILE = os.path.join(CONFIG_DIR, 'connections.dat')

# Define themes directory
THEMES_DIR = os.path.join(CONFIG_DIR, 'themes')

# Ensure the themes directory exists
os.makedirs(THEMES_DIR, exist_ok=True)

# Development themes directory
DEV_THEMES_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'themes')

# Global DEV flag
DEV = True  # Set this to False for production

# Add this new function at the top level of the module
def initialize_config():
    """Initialize the configuration and ensure themes are set up."""
    ensure_themes_dir()
    config = load_config()
    return config

def ensure_themes_dir():
    """Ensure the themes directory exists and is populated."""
    os.makedirs(THEMES_DIR, exist_ok=True)
    global DEV
    if DEV:
        print(f"Copying themes from {DEV_THEMES_DIR} to {THEMES_DIR} in DEV mode")
        for theme in os.listdir(DEV_THEMES_DIR):
            theme_path = os.path.join(DEV_THEMES_DIR, theme)
            if os.path.isdir(theme_path):
                dest_path = os.path.join(THEMES_DIR, theme)
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(theme_path, dest_path)
    else:
        # Only copy if the destination doesn't exist
        for theme in os.listdir(DEV_THEMES_DIR):
            theme_path = os.path.join(DEV_THEMES_DIR, theme)
            if os.path.isdir(theme_path):
                dest_path = os.path.join(THEMES_DIR, theme)
                if not os.path.exists(dest_path):
                    shutil.copytree(theme_path, dest_path)

def load_or_generate_key():
    key = keyring.get_password(APP_NAME, KEY_ID)
    if not key:
        key = Fernet.generate_key()
        keyring.set_password(APP_NAME, KEY_ID, key.decode())
        print("New key generated and stored in system keyring.")
    return key.encode() if isinstance(key, str) else key

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

def load_theme(theme_name):
    """Load a theme from its directory."""
    theme_dir = os.path.join(THEMES_DIR, theme_name)
    
    if not os.path.exists(theme_dir):
        # If the theme doesn't exist in the runtime directory, copy it from the development directory
        dev_theme_dir = os.path.join(DEV_THEMES_DIR, theme_name)
        if os.path.exists(dev_theme_dir):
            shutil.copytree(dev_theme_dir, theme_dir)
        else:
            print(f"Theme '{theme_name}' not found in development or runtime directories.")
            return None

    style_file = os.path.join(theme_dir, 'styles.json')
    if os.path.exists(style_file):
        with open(style_file, 'r') as f:
            theme_data = json.load(f)
        
        # Update image paths to be absolute
        for key, value in theme_data.items():
            if isinstance(value, str) and value.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                theme_data[key] = os.path.join(theme_dir, value)
        
        return theme_data
    else:
        print(f"styles.json not found for theme '{theme_name}'")
        return None

def find_terminals():
    common_terminal_names = {
        "XTerm": ("xterm", ["-hold", "-e"], False),
        "GNOME Terminal": ("gnome-terminal", ["--", "bash", "-c"], True),
        "Konsole": ("konsole", ["-e", "bash", "-c"], True),
        "XFCE Terminal": ("xfce4-terminal", ["--hold", "-e"], True),
        "LXTerminal": ("lxterminal", ["-e", "bash", "-c"], True),
        "Tilix": ("tilix", ["-e", "bash", "-c"], True),
        "Alacritty": ("alacritty", ["-e", "bash", "-c"], True),
        "Kitty": ("kitty", ["bash", "-c"], True),
        "URxvt": ("urxvt", ["-hold", "-e"], False),
        "st": ("st", ["-e", "bash", "-c"], True),
        "Eterm": ("eterm", ["-e", "bash", "-c"], True),
        "Mate Terminal": ("mate-terminal", ["-e", "bash", "-c"], True)
    }

    available_terminal_emulators = {}

    for name, (command, args, use_single_arg) in common_terminal_names.items():
        if shutil.which(command):
            available_terminal_emulators[name] = (command, args, use_single_arg)
    return available_terminal_emulators