import json
import os
from cryptography.fernet import Fernet

KEY_FILE = '.nuTTY_key'
CONFIG_FILE = 'config.json'  # Config file for storing persistent data

def load_or_generate_key():
    """Load the secret key from a file or generate a new one if it doesn't exist."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
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
