from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, 
    QPushButton, QHBoxLayout, QDialog, QLabel, QComboBox, 
    QMessageBox, QSystemTrayIcon
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from tray import create_tray_manager
from model import ConnectionListModel
from dialogs import AddConnectionDialog, EditConnectionDialog, AboutDialog
from config import save_config, get_connections_file_path
import json
import subprocess
import os
import shutil
from delegates import ConnectionItemDelegate


class MainWindow(QMainWindow):
    def __init__(self, config, cipher_suite):
        super().__init__()
        self.config = config
        self.cipher_suite = cipher_suite
        self.available_terminal_emulators = {}
        # Setup the main window
        self.setWindowTitle("nuTTY")
        self.setGeometry(300, 200, 600, 400)
        # Set the window icon
        self.setWindowIcon(QIcon('assets/icons/nuTTY_64x64_dark.png'))  # Replace with the path to your icon

        # Central widget layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Replace QTableWidget with QListView
        self.connection_list_view = QListView()
        self.connection_list_model = ConnectionListModel()  # Using the custom model
        self.connection_list_view.setModel(self.connection_list_model)
        self.layout.addWidget(self.connection_list_view)

        # Connect the double-click event to connect_to_server
        self.connection_list_view.doubleClicked.connect(self.connect_to_server)

        # Buttons for adding/removing connections
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.add_btn.clicked.connect(self.add_connection)
        self.remove_btn = QPushButton("-")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_connection)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.connect_to_server)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_connection)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.connect_btn)
        self.layout.addLayout(btn_layout)

        # Use the custom delegate for the connection list view
        self.connection_list_view.setItemDelegate(ConnectionItemDelegate())

        # Enable/disable buttons based on selection
        self.connection_list_view.selectionModel().selectionChanged.connect(self.update_button_states)
        
        # Load the terminal emulator from config.json
        self.find_terminals()
        self.terminal_executable = self.config.get("terminal_emulator", "xfce4-terminal")  # Default to xfce4-terminal TODO: default to system default terminal emulator
        self.ssh_command_template = 'ssh {username}@{domain}'  # SSH command template
        
        # Load connections
        self.load_connections()
        
        # System tray setup
        self.tray_manager = create_tray_manager(self, self.connection_list_model)
        self.tray_manager.show_window_signal.connect(self.show)
        self.tray_manager.exit_app_signal.connect(self.exit_app)
        self.tray_manager.connect_to_server_signal.connect(self.connect_to_server_from_tray)

        # Create the menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        select_close_window_action = file_menu.addAction("Close Window")
        select_close_window_action.triggered.connect(self.close)
        select_close_window_action = file_menu.addAction("Exit")
        select_close_window_action.triggered.connect(self.exit_app)

        # Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        select_emulator_action = settings_menu.addAction("Select Emulator")
        select_emulator_action.triggered.connect(self.select_terminal_emulator)
        minimize_on_close_action = settings_menu.addAction("Minimize to Tray on Close")
        minimize_on_close_action.setCheckable(True)
        minimize_on_close_action.setChecked(self.config.get("minimize_on_close", True))
        minimize_on_close_action.toggled.connect(self.toggle_minimize_on_close)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About nuTTY")
        about_action.triggered.connect(self.show_about)


    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()


    def find_terminals(self):
        # List of common terminal emulators with their names and commands
        self.common_terminal_names = {
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

        self.available_terminal_emulators = {}

        # Check if the terminal emulator command is available in the system PATH
        for name, (command, _) in self.common_terminal_names.items():
            if shutil.which(command):  # Check if the terminal command is available
                self.available_terminal_emulators[name] = (command, self.common_terminal_names[name][1])  # Add to available terminals

    def add_connection(self):
        dialog = AddConnectionDialog(self)
        if dialog.exec_():
            # Get connection details from the dialog
            connection = dialog.get_connection_details()

            # Add the new connection to the model
            self.connection_list_model.add_connection(connection)

            # Save the new connections to the file (since the list has changed)
            self.save_connections()

            # Update the tray menu with the new connection
            self.tray_manager.update_tray_connections()

    def save_connections(self):
        connections = []
        # Iterate over the model to get all connections
        for row in range(self.connection_list_model.rowCount()):
            connection = self.connection_list_model.get_connection(row)
            # Create a copy of the connection to avoid modifying the original
            connection_copy = connection.copy()
            # Encrypt the password if it exists
            if connection_copy.get('password'):
                connection_copy['password'] = self.cipher_suite.encrypt(connection_copy['password'].encode()).decode()
            connections.append(connection_copy)

        # Encrypt and save the connection data
        encrypted_data = self.cipher_suite.encrypt(json.dumps(connections).encode())
        with open(get_connections_file_path(), 'wb') as f:
            f.write(encrypted_data)


    def load_connections(self):
        try:
            # Read and decrypt the connection data from file
            connections_file = get_connections_file_path()
            if os.path.exists(connections_file):
                with open(connections_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()

                # Parse the JSON data
                connections = json.loads(decrypted_data)

                # Add the connections to the model
                for connection in connections:
                    self.connection_list_model.add_connection(connection)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading connections: {e}")
            
    def remove_connection(self):
        # Get the selected row in the QListView
        selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
        
        if selected_indexes:
            # Ask the user for confirmation before removing
            confirm = QMessageBox.question(self, "Delete Connection", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                # Remove the selected connection from the model
                selected_row = selected_indexes[0].row()  # Get the row of the selected item
                self.connection_list_model.remove_connection(selected_row)  # Use the model's remove method
                
                # Save the updated connection list to the file
                self.save_connections()

                # Update the tray menu after removing a connection
                self.update_tray_connections(self.tray_icon.contextMenu())


    def connect_to_server(self):
        # Get the selected connection's index
        selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()

        if selected_indexes:
            selected_row = selected_indexes[0].row()
            # Retrieve the selected connection details
            connection = self.connection_list_model.get_connection(selected_row)

            if connection['protocol'] == 'SSH':
                command = self.format_ssh_command(connection)
            elif connection['protocol'] == 'Telnet':
                command = self.format_telnet_command(connection)
            else:
                QMessageBox.critical(self, "Error", f"Unsupported protocol: {connection['protocol']}")
                return

            # Get the proper terminal command string format for the selected terminal emulator
            terminal_format = self.available_terminal_emulators[self.terminal_executable][1]

            # Format the terminal command with the connection command
            terminal_command = terminal_format.format(ssh_command=command)

            try:
                # Execute the terminal command
                subprocess.Popen(terminal_command, shell=True)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

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
        telnet_command = f"telnet {connection['domain']}"
        
        if connection.get('username') or connection.get('password'):
            QMessageBox.warning(self, "Warning", "Telnet doesn't support secure authentication. Username and password will be sent in plain text.")
        
        return telnet_command




    def update_button_states(self):
        # Check if any connection is selected
        has_selection = len(self.connection_list_view.selectionModel().selectedIndexes()) > 0

        # Enable/disable buttons based on whether a connection is selected
        self.remove_btn.setEnabled(has_selection)
        self.connect_btn.setEnabled(has_selection)
        self.edit_btn.setEnabled(has_selection)


    def toggle_minimize_on_close(self, checked):
        """Update the 'minimize on close' setting."""
        self.config['minimize_on_close'] = checked
        save_config(self.config)

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of exiting."""
        if self.config.get("minimize_on_close", True):
            event.ignore()
            self.hide()
            self.tray_manager.show_message(
                "nuTTY SSH Manager",
                "Application minimized to tray.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.exit_app()

    def exit_app(self):
        """Exit the application completely."""
        self.tray_manager.hide_tray_icon()
        QApplication.quit()  # Quit the application

    def select_terminal_emulator(self):
        # Dialog to choose the preferred terminal emulator
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Terminal Emulator")
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Choose Terminal Emulator:")
        layout.addWidget(label)

        emulator_options = QComboBox()

        # Iterate over the keys of the available_terminal_emulators dictionary
        for name in self.available_terminal_emulators.keys():
            emulator_options.addItem(name)

        layout.addWidget(emulator_options)


        # Set the current selection to the previously chosen terminal emulator
        for index, (name, (command, _)) in enumerate(self.available_terminal_emulators.items()):
            if command == self.terminal_executable:
                emulator_options.setCurrentIndex(index)


        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.set_terminal_emulator(dialog, emulator_options.currentIndex()))
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        dialog.exec_()

    def set_terminal_emulator(self, dialog, selected_index):
        """Set the terminal emulator based on the selected index."""
        # Get the terminal name from the QComboBox by index
        terminal_name = dialog.findChild(QComboBox).itemText(selected_index)

        # Set the selected terminal name (not the command)
        self.terminal_executable = terminal_name

        # Save the new terminal emulator in config.json
        self.config['terminal_emulator'] = self.terminal_executable
        save_config(self.config)

        dialog.accept()

    def edit_connection(self):
        # Get the selected connection's index
        selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
        
        if selected_indexes:
            selected_row = selected_indexes[0].row()
            # Retrieve the selected connection details
            connection = self.connection_list_model.get_connection(selected_row)
            
            # Open the edit dialog
            dialog = EditConnectionDialog(self, connection)
            if dialog.exec_():
                # Get updated connection details from the dialog
                updated_connection = dialog.get_connection_details()
                
                # Update the connection in the model
                self.connection_list_model.update_connection(selected_row, updated_connection)
                
                # Save the updated connections to the file
                self.save_connections()
                
                # Update the tray menu
                self.tray_manager.update_tray_connections()

    def connect_to_server_from_tray(self, row):
        """Connect to a server from the tray menu based on the row index."""
        if row >= 0:
            # Retrieve the connection details
            connection = self.connection_list_model.get_connection(row)
            username = connection['username']
            domain = connection['domain']

            # Format the SSH command
            ssh_command = self.ssh_command_template.format(username=username, domain=domain)

            # Get the proper terminal command string format for the selected terminal emulator
            terminal_format = self.available_terminal_emulators[self.terminal_executable][1]

            # Format the terminal command with the SSH command
            terminal_command = terminal_format.format(ssh_command=ssh_command)

            try:
                # Execute the terminal command
                subprocess.Popen(terminal_command, shell=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

    # Add other necessary methods here (e.g., find_terminals, load_connections, create_menu_bar, etc.)

