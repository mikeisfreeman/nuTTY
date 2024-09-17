from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, 
    QPushButton, QHBoxLayout, QDialog, QLabel, QComboBox, 
    QMessageBox, QSystemTrayIcon,QMenuBar, QAction
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
from themes import ThemeDialog

def create_menu_bar(parent: QMainWindow):
    menu_bar = parent.menuBar()

    # File menu
    file_menu = menu_bar.addMenu("File")
    close_window_action = file_menu.addAction("Close Window")
    close_window_action.triggered.connect(parent.close)
    exit_action = file_menu.addAction("Exit")
    exit_action.triggered.connect(parent.exit_app)

    # Settings menu
    settings_menu = menu_bar.addMenu("Settings")
    preferences_action = settings_menu.addAction("Preferences")
    preferences_action.triggered.connect(parent.show_preferences)

    # Help menu
    help_menu = menu_bar.addMenu("Help")
    about_action = help_menu.addAction("About nuTTY")
    about_action.triggered.connect(parent.show_about)

    return menu_bar