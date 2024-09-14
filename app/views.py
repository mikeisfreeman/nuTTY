from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, 
    QPushButton, QHBoxLayout, QDialog, QLabel, QComboBox, 
    QMessageBox, QSystemTrayIcon
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from tray import create_tray_manager
from model import ConnectionListModel
from dialogs import AddConnectionDialog, EditConnectionDialog

from delegates import ConnectionItemDelegate
from menu_bar import create_menu_bar
from controller import Controller

class MainWindow(QMainWindow):
    def __init__(self, config, cipher_suite):
        super().__init__()
        self.controller = Controller(config, cipher_suite)
        self.config = config
        # Setup the main window
        self.setWindowTitle("nuTTY")
        self.setGeometry(300, 200, 600, 400)
        self.setWindowIcon(QIcon('assets/icons/nuTTY_64x64_dark.png'))

        # Central widget layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Replace QTableWidget with QListView
        self.connection_list_view = QListView()
        self.connection_list_view.setModel(self.controller.connection_list_model)
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
        
        # System tray setup
        self.tray_manager = create_tray_manager(self, self.controller.connection_list_model)
        self.tray_manager.show_window_signal.connect(self.show)
        self.tray_manager.exit_app_signal.connect(self.exit_app)
        self.tray_manager.connect_to_server_signal.connect(self.connect_to_server_from_tray)

        # Create the menu bar
        create_menu_bar(self)

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def add_connection(self):
        dialog = AddConnectionDialog(self)
        if dialog.exec_():
            connection = dialog.get_connection_details()
            self.controller.add_connection(connection)
            self.tray_manager.update_tray_connections()

    def remove_connection(self):
        selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
        if selected_indexes:
            confirm = QMessageBox.question(self, "Delete Connection", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                selected_row = selected_indexes[0].row()
                self.controller.remove_connection(selected_row)
                self.tray_manager.update_tray_connections()

    def connect_to_server(self):
        selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
        if selected_indexes:
            selected_row = selected_indexes[0].row()
            connection = self.controller.connection_list_model.get_connection(selected_row)
            try:
                self.controller.connect_to_server(connection)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_connection(self):
        selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
        if selected_indexes:
            selected_row = selected_indexes[0].row()
            connection = self.controller.connection_list_model.get_connection(selected_row)
            dialog = EditConnectionDialog(self, connection)
            if dialog.exec_():
                updated_connection = dialog.get_connection_details()
                self.controller.update_connection(selected_row, updated_connection)
                self.tray_manager.update_tray_connections()

    def select_terminal_emulator(self):
        # Dialog to choose the preferred terminal emulator
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Terminal Emulator")
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Choose Terminal Emulator:")
        layout.addWidget(label)

        emulator_options = QComboBox()

        # Iterate over the keys of the available_terminal_emulators dictionary
        for name in self.controller.available_terminal_emulators.keys():
            emulator_options.addItem(name)

        layout.addWidget(emulator_options)

        # Set the current selection to the previously chosen terminal emulator
        for index, (name, (command, _)) in enumerate(self.controller.available_terminal_emulators.items()):
            if command == self.controller.terminal_executable:
                emulator_options.setCurrentIndex(index)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.set_terminal_emulator(dialog, emulator_options.currentIndex()))
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        if dialog.exec_():
            selected_terminal = emulator_options.currentText()
            self.controller.set_terminal_emulator(selected_terminal)

    def set_terminal_emulator(self, dialog, selected_index):
        """Set the terminal emulator based on the selected index."""
        # Get the terminal name from the QComboBox by index
        terminal_name = dialog.findChild(QComboBox).itemText(selected_index)

        # Set the selected terminal name (not the command)
        self.controller.set_terminal_emulator(terminal_name)

        dialog.accept()

    def update_button_states(self):
        # Check if any connection is selected
        has_selection = len(self.connection_list_view.selectionModel().selectedIndexes()) > 0

        # Enable/disable buttons based on whether a connection is selected
        self.remove_btn.setEnabled(has_selection)
        self.connect_btn.setEnabled(has_selection)
        self.edit_btn.setEnabled(has_selection)

    def toggle_minimize_on_close(self, checked):
        self.controller.toggle_minimize_on_close(checked)

    def closeEvent(self, event):
        if self.controller.get_minimize_on_close():
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

    def connect_to_server_from_tray(self, row):
        """Connect to a server from the tray menu based on the row index."""
        if row >= 0:
            # Retrieve the connection details
            connection = self.controller.connection_list_model.get_connection(row)
            try:
                self.controller.connect_to_server(connection)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

