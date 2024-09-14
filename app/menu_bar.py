
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, 
    QPushButton, QHBoxLayout, QDialog, QLabel, QComboBox, 
    QMessageBox, QSystemTrayIcon,QMenuBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from tray import create_tray_manager
from model import ConnectionListModel
from dialogs import AddConnectionDialog, EditConnectionDialog, AboutDialog
from config import save_config, get_connections_file_path, find_terminals
import json
import subprocess
import os
import shutil
from delegates import ConnectionItemDelegate


def create_menu_bar(parent: QMainWindow):
        menu_bar = parent.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        select_close_window_action = file_menu.addAction("Close Window")
        select_close_window_action.triggered.connect(parent.close)
        select_close_window_action = file_menu.addAction("Exit")
        select_close_window_action.triggered.connect(parent.exit_app)

        # Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        select_emulator_action = settings_menu.addAction("Select Emulator")
        select_emulator_action.triggered.connect(parent.select_terminal_emulator)
        minimize_on_close_action = settings_menu.addAction("Minimize to Tray on Close")
        minimize_on_close_action.setCheckable(True)
        minimize_on_close_action.setChecked(parent.config.get("minimize_on_close", True))
        minimize_on_close_action.toggled.connect(parent.toggle_minimize_on_close)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About nuTTY")
        about_action.triggered.connect(parent.show_about)