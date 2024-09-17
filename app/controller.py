from PyQt5.QtWidgets import QMessageBox
from model import ConnectionListModel
from config import save_config, get_connections_file_path, find_terminals, load_theme
import json
import subprocess
import os
import shutil
import logging

class Controller:
    def __init__(self, config, cipher_suite):
        self.config = config
        self.cipher_suite = cipher_suite
        self.connection_list_model = ConnectionListModel(self.load_connections())
        self.available_terminal_emulators = find_terminals()
        self.terminal_executable = self.get_terminal_executable()

    def load_connections(self):
        connections_file = get_connections_file_path()
        if os.path.exists(connections_file):
            with open(connections_file, 'r') as f:
                encrypted_data = f.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode()).decode()
                return json.loads(decrypted_data)
        return []

    def save_connections(self):
        connections_file = get_connections_file_path()
        encrypted_data = self.cipher_suite.encrypt(json.dumps(self.connection_list_model.connections).encode())
        with open(connections_file, 'w') as f:
            f.write(encrypted_data.decode())

    def add_connection(self, connection):
        self.connection_list_model.add_connection(connection)
        self.save_connections()

    def remove_connection(self, index):
        self.connection_list_model.remove_connection(index)
        self.save_connections()

    def update_connection(self, index, connection):
        self.connection_list_model.update_connection(index, connection)
        self.save_connections()

    def duplicate_connection(self, index):
        connection = self.connection_list_model.get_connection(index).copy()
        connection['name'] = f"{connection['name']} (Copy)"
        self.add_connection(connection)

    def connect_to_server(self, connection):
        command = self.build_ssh_command(connection)
        try:
            subprocess.Popen(command, shell=False)
        except Exception as e:
            logging.error(f"Failed to connect to server: {str(e)}")
            raise

    def build_ssh_command(self, connection):
        terminal_name = self.config.get('terminal_emulator')
        terminal_info = self.available_terminal_emulators.get(terminal_name)
        if not terminal_info:
            raise ValueError(f"Terminal emulator '{terminal_name}' not found")

        command, args, use_single_arg = terminal_info
        ssh_command = [command]
        ssh_command.extend(args)

        ssh_args = ["ssh"]
        if connection.get('x11', False):
            ssh_args.append("-X")
        if connection.get('use_identity_file', False) and connection.get('identity_file'):
            ssh_args.extend(["-i", connection['identity_file']])
        ssh_args.append(f"{connection['username']}@{connection['domain']}")

        if use_single_arg:
            ssh_command.append(" ".join(ssh_args))
        else:
            ssh_command.extend(ssh_args)

        return ssh_command

    def get_terminal_executable(self):
        terminal_name = self.config.get('terminal_emulator')
        if terminal_name in self.available_terminal_emulators:
            return self.available_terminal_emulators[terminal_name][0]
        if self.available_terminal_emulators:
            first_terminal = next(iter(self.available_terminal_emulators))
            return self.available_terminal_emulators[first_terminal][0]
        return 'xterm'

    def set_terminal_emulator(self, terminal_name):
        if terminal_name in self.available_terminal_emulators:
            self.terminal_executable = self.available_terminal_emulators[terminal_name][0]
            self.config['terminal_emulator'] = terminal_name
            save_config(self.config)

    def get_minimize_on_close(self):
        return self.config.get('minimize_on_close', False)

    def toggle_minimize_on_close(self, value):
        self.config['minimize_on_close'] = value
        save_config(self.config)

    def get_available_themes(self):
        return self.get_available_themes()

    def set_theme(self, theme_name):
        self.config['theme'] = theme_name
        save_config(self.config)
        return load_theme(theme_name)

    def get_current_theme(self):
        return self.config.get('theme', 'coffee')
