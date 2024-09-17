from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, 
    QPushButton, QHBoxLayout, QDialog, QLabel, QComboBox, 
    QMessageBox, QSystemTrayIcon, QStyleFactory, QMenu
)
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon
from tray import create_tray_manager
from dialogs import AddConnectionDialog, EditConnectionDialog, AboutDialog
from delegates import ConnectionItemDelegate
from menu_bar import create_menu_bar
from controller import Controller
from config import load_theme, save_config
from preferences_dialog import PreferencesDialog
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    def __init__(self, config, cipher_suite):
        try:
            super().__init__()
            self.controller = Controller(config, cipher_suite)
            self.config = config
            self.theme_data = {}
            
            self.current_theme = config.get('theme', 'coffee')
            self.theme_data = load_theme(self.current_theme)
            
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            
            self.setWindowTitle("nuTTY")
            self.setFixedSize(400, 700)
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
            self.setWindowIcon(QIcon('assets/icons/nuTTY_64x64_dark.png'))

            # Prevent resizing
            self.setMinimumSize(400, 700)
            self.setMaximumSize(400, 700)

            # Central widget layout
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)

            # Connection list view
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

            self.duplicate_btn = QPushButton("Duplicate")
            self.duplicate_btn.setEnabled(False)
            self.duplicate_btn.clicked.connect(self.duplicate_connection)

            btn_layout.addWidget(self.add_btn)
            btn_layout.addWidget(self.remove_btn)
            btn_layout.addWidget(self.edit_btn)
            btn_layout.addWidget(self.duplicate_btn)
            btn_layout.addWidget(self.connect_btn)
            self.layout.addLayout(btn_layout)

            # Use the custom delegate for the connection list view
            self.connection_list_view.setItemDelegate(ConnectionItemDelegate(self.theme_data))

            # Enable/disable buttons based on selection
            self.connection_list_view.selectionModel().selectionChanged.connect(self.update_button_states)
            
            # System tray setup
            self.tray_manager = create_tray_manager(self, self.controller.connection_list_model)
            self.tray_manager.show_window_signal.connect(self.show)
            self.tray_manager.exit_app_signal.connect(self.exit_app)
            self.tray_manager.connect_to_server_signal.connect(self.connect_to_server_from_tray)

            # Create the menu bar
            create_menu_bar(self)

            # Apply the initial theme
            self.apply_theme(self.theme_data)
            
            # Re-save connections to ensure they're encrypted with the new key
            self.controller.save_connections()

        except Exception as e:
            logging.error(f"Error initializing MainWindow: {str(e)}")
            QMessageBox.critical(self, "Initialization Error", f"An error occurred while starting the application: {str(e)}")
            raise


    def apply_theme(self, theme_data):
        self.theme_data = theme_data  # Store the original theme data
        if not theme_data:
            return

        # Apply global styles
        global_style = "QWidget { "
        for key, value in theme_data.items():
            if key.startswith("global_"):
                global_style += f"{key.replace('global_', '')}: {value}; "
        global_style += "}"
        
        # Apply window styles
        window_style = "QMainWindow { "
        for key, value in theme_data.items():
            if key.startswith("window_"):
                if key == "window_background-image":
                    window_style += f"background-image: {value}; "
                    window_style += "background-position: center; "
                    window_style += "background-repeat: no-repeat; "
                    window_style += "background-attachment: fixed; "
                else:
                    window_style += f"{key.replace('window_', '')}: {value}; "
        window_style += "}"
        
        # Set the window style
        self.setStyleSheet(window_style)
        
        # Apply QListView styles
        list_view_style = "QListView { "
        for key, value in theme_data.items():
            if key.startswith("list_view_") and not key.startswith("list_view_item_"):
                list_view_style += f"{key.replace('list_view_', '')}: {value}; "
        list_view_style += "} "
        
        # Apply QListView item styles
        list_view_style += "QListView::item { "
        for key, value in theme_data.items():
            if key.startswith("list_view_item_") and not key.startswith("list_view_item_selected_"):
                list_view_style += f"{key.replace('list_view_item_', '')}: {value}; "
        list_view_style += "} "
        
        # Apply QListView selected item styles
        list_view_style += "QListView::item:selected { "
        for key, value in theme_data.items():
            if key.startswith("list_view_item_selected_"):
                list_view_style += f"{key.replace('list_view_item_selected_', '')}: {value}; "
        list_view_style += "}"
        
        self.connection_list_view.setStyleSheet(list_view_style)

        # Apply QPushButton styles
        button_style = "QPushButton { "
        for key, value in theme_data.items():
            if key.startswith("button_") and not any(x in key for x in ["hover", "pressed", "disabled"]):
                button_style += f"{key.replace('button_', '')}: {value}; "
        button_style += "} "
        
        # Apply QPushButton hover styles
        button_style += "QPushButton:hover { "
        for key, value in theme_data.items():
            if key.startswith("button_hover_"):
                button_style += f"{key.replace('button_hover_', '')}: {value}; "
        button_style += "} "
        
        # Apply QPushButton pressed styles
        button_style += "QPushButton:pressed { "
        for key, value in theme_data.items():
            if key.startswith("button_pressed_"):
                button_style += f"{key.replace('button_pressed_', '')}: {value}; "
        button_style += "} "
        
        # Apply QPushButton disabled styles
        button_style += "QPushButton:disabled { "
        for key, value in theme_data.items():
            if key.startswith("button_disabled_"):
                button_style += f"{key.replace('button_disabled_', '')}: {value}; "
        button_style += "}"
        
        for button in [self.add_btn, self.remove_btn, self.connect_btn, self.edit_btn, self.duplicate_btn]:
            button.setStyleSheet(button_style)

        # Apply QMenuBar styles
        menu_bar_style = "QMenuBar { "
        menu_bar_style += f"background-color: {theme_data.get('global_background-color', '#000000')}; "
        menu_bar_style += f"color: {theme_data.get('global_color', '#00ff00')}; "
        menu_bar_style += f"border-bottom: {theme_data.get('menu_border',  '1px solid #00ff00')}; "
        menu_bar_style += "} "
        
        menu_bar_style += "QMenuBar::item { "
        menu_bar_style += "background-color: transparent; "
        menu_bar_style += "} "
        
        menu_bar_style += "QMenuBar::item:selected { "
        menu_bar_style += f"background-color: {theme_data.get('list_view_item_selected_background-color', 'rgba(0, 80, 0, 200)')}; "
        menu_bar_style += "} "
        
        self.menuBar().setStyleSheet(menu_bar_style)

        # Apply QMenu styles
        menu_style = "QMenu { "
        menu_style += f"background-color: {theme_data.get('global_background-color', '#000000')}; "
        menu_style += f"color: {theme_data.get('global_color', '#00ff00')}; "
        menu_style += f"border: {theme_data.get('menu_border',  '1px solid #00ff00')}; "
        menu_style += "} "
        
        menu_style += "QMenu::item { "
        menu_style += "background-color: transparent; "
        menu_style += "} "
        
        menu_style += "QMenu::item:selected { "
        menu_style += f"background-color: {theme_data.get('list_view_item_selected_background-color', 'rgba(0, 80, 0, 200)')}; "
        menu_style += "} "
        
        # Apply to all menus
        for menu in self.menuBar().findChildren(QMenu):
            menu.setStyleSheet(menu_style)

        # Update the delegate with the original theme data
        
        self.connection_list_view.setItemDelegate(ConnectionItemDelegate(self.theme_data))

        # Save the current theme
        self.current_theme = theme_data.get('name', 'darcula')
        self.config['theme'] = self.current_theme
        save_config(self.config)

    def add_connection(self):
        try:
            dialog = AddConnectionDialog(self)
            if dialog.exec_():
                connection = dialog.get_connection_details()
                self.controller.add_connection(connection)
                self.tray_manager.update_tray_connections()
        except Exception as e:
            logging.error(f"Error adding connection: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add connection: {str(e)}")

    def remove_connection(self):
        try:
            selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
            if selected_indexes:
                confirm = QMessageBox.question(self, "Delete Connection", "Confirm deletion?  This cannot be undone", QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    selected_row = selected_indexes[0].row()
                    self.controller.remove_connection(selected_row)
                    self.tray_manager.update_tray_connections()
        except Exception as e:
            logging.error(f"Error removing connection: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove connection: {str(e)}")

    def connect_to_server(self):
        try:
            selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
            if selected_indexes:
                selected_row = selected_indexes[0].row()
                connection = self.controller.connection_list_model.get_connection(selected_row)
                self.controller.connect_to_server(connection)
        except Exception as e:
            logging.error(f"Error connecting to server: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to connect to server: {str(e)}")

    def edit_connection(self):
        try:
            selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
            if selected_indexes:
                selected_row = selected_indexes[0].row()
                connection = self.controller.connection_list_model.get_connection(selected_row)
                dialog = EditConnectionDialog(self, connection)
                if dialog.exec_():
                    updated_connection = dialog.get_connection_details()
                    self.controller.update_connection(selected_row, updated_connection)
                    self.tray_manager.update_tray_connections()
        except Exception as e:
            logging.error(f"Error editing connection: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit connection: {str(e)}")

    def duplicate_connection(self):
        try:
            selected_indexes = self.connection_list_view.selectionModel().selectedIndexes()
            if selected_indexes:
                selected_row = selected_indexes[0].row()
                self.controller.duplicate_connection(selected_row)
                self.tray_manager.update_tray_connections()
        except Exception as e:
            logging.error(f"Error duplicating connection: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to duplicate connection: {str(e)}")

    def select_terminal_emulator(self):
        try:
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
        except Exception as e:
            logging.error(f"Error selecting terminal emulator: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to select terminal emulator: {str(e)}")

    def set_terminal_emulator(self, dialog, selected_index):
        try:
            """Set the terminal emulator based on the selected index."""
            # Get the terminal name from the QComboBox by index
            terminal_name = dialog.findChild(QComboBox).itemText(selected_index)

            # Set the selected terminal name (not the command)
            self.controller.set_terminal_emulator(terminal_name)

            dialog.accept()
        except Exception as e:
            logging.error(f"Error setting terminal emulator: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to set terminal emulator: {str(e)}")

    def update_button_states(self):
        try:
            # Check if any connection is selected
            has_selection = len(self.connection_list_view.selectionModel().selectedIndexes()) > 0

            # Enable/disable buttons based on whether a connection is selected
            self.remove_btn.setEnabled(has_selection)
            self.connect_btn.setEnabled(has_selection)
            self.edit_btn.setEnabled(has_selection)
            self.duplicate_btn.setEnabled(has_selection)
        except Exception as e:
            logging.error(f"Error updating button states: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to update button states: {str(e)}")

    def toggle_minimize_on_close(self, checked):
        try:
            self.controller.toggle_minimize_on_close(checked)
        except Exception as e:
            logging.error(f"Error toggling minimize on close: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to toggle minimize on close: {str(e)}")

    def closeEvent(self, event):
        try:
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
        except Exception as e:
            logging.error(f"Error handling close event: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while closing the application: {str(e)}")

    def exit_app(self):
        try:
            """Exit the application completely."""
            self.tray_manager.hide_tray_icon()
            QApplication.quit()  # Quit the application
        except Exception as e:
            logging.error(f"Error exiting application: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to exit application: {str(e)}")

    def connect_to_server_from_tray(self, row):
        try:
            """Connect to a server from the tray menu based on the row index."""
            if row >= 0:
                # Retrieve the connection details
                connection = self.controller.connection_list_model.get_connection(row)
                self.controller.connect_to_server(connection)
        except Exception as e:
            logging.error(f"Error connecting to server from tray: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to connect to server from tray: {str(e)}")

    def show_about(self):
        try:
            """Show the About dialog."""
            about_dialog = AboutDialog(self)
            about_dialog.exec_()
        except Exception as e:
            logging.error(f"Error showing About dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to show About dialog: {str(e)}")

    def show_preferences(self):
        try:
            preferences_dialog = PreferencesDialog(self)
            preferences_dialog.exec_()
        except Exception as e:
            logging.error(f"Error showing Preferences dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to show Preferences dialog: {str(e)}")

    

