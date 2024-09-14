from PyQt5.QtWidgets import QMessageBox
from model import ConnectionListModel
from config import save_config, get_connections_file_path, find_terminals
from tray import create_tray_manager
import json
import subprocess
import os

class Controller:
    def __init__(self, config, cipher_suite):
        self.config = config
        self.cipher_suite = cipher_suite
        self.connection_list_model = ConnectionListModel()
        self.available_terminal_emulators = find_terminals()
        self.terminal_executable = self.config.get("terminal_emulator", "xfce4-terminal")
        self.ssh_command_template = 'ssh {username}@{domain}'
        self.load_connections()

    def load_connections(self):
        try:
            connections_file = get_connections_file_path()
            if os.path.exists(connections_file):
                with open(connections_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
                connections = json.loads(decrypted_data)
                for connection in connections:
                    self.connection_list_model.add_connection(connection)
        except Exception as e:
            print(f"Error loading connections: {e}")

    def save_connections(self):
        connections = []
        for row in range(self.connection_list_model.rowCount()):
            connection = self.connection_list_model.get_connection(row)
            connection_copy = connection.copy()
            if connection_copy.get('password'):
                connection_copy['password'] = self.cipher_suite.encrypt(connection_copy['password'].encode()).decode()
            connections.append(connection_copy)

        encrypted_data = self.cipher_suite.encrypt(json.dumps(connections).encode())
        with open(get_connections_file_path(), 'wb') as f:
            f.write(encrypted_data)

    def add_connection(self, connection):
        self.connection_list_model.add_connection(connection)
        self.save_connections()

    def remove_connection(self, row):
        self.connection_list_model.remove_connection(row)
        self.save_connections()

    def update_connection(self, row, connection):
        self.connection_list_model.update_connection(row, connection)
        self.save_connections()

    def connect_to_server(self, connection):
        if connection['protocol'] == 'SSH':
            command = self.format_ssh_command(connection)
        elif connection['protocol'] == 'Telnet':
            command = self.format_telnet_command(connection)
        else:
            raise ValueError(f"Unsupported protocol: {connection['protocol']}")

        terminal_format = self.available_terminal_emulators[self.terminal_executable][1]
        terminal_command = terminal_format.format(ssh_command=command)

        try:
            subprocess.Popen(terminal_command, shell=True)
        except Exception as e:
            raise RuntimeError(f"Failed to execute command: {e}")

    def format_ssh_command(self, connection):
        ssh_command = f"ssh {connection['username']}@{connection['domain']}"

        if connection.get('use_identity_file') and connection.get('identity_file'):
            ssh_command += f" -i {connection['identity_file']}"
        elif connection.get('password'):
            ssh_command = f"sshpass -p {connection['password']} {ssh_command}"

        if connection.get('x11'):
            ssh_command += " -X"

        return ssh_command

    def format_telnet_command(self, connection):
        return f"telnet {connection['domain']}"

    def set_terminal_emulator(self, terminal_name):
        self.terminal_executable = terminal_name
        self.config['terminal_emulator'] = self.terminal_executable
        save_config(self.config)

    def toggle_minimize_on_close(self, checked):
        self.config['minimize_on_close'] = checked
        save_config(self.config)

    def get_minimize_on_close(self):
        return self.config.get("minimize_on_close", True)
