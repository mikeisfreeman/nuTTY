from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QCheckBox, 
                             QDialogButtonBox, QWidget)
from PyQt5.QtCore import Qt
import os
from config import THEMES_DIR, load_theme

class PreferencesDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.setFixedSize(300, 250)  # Set a fixed size for the dialog
        
        # Set window flags to remove resize handles
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Create a main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins from the main layout
        
        # Create a widget to hold the content
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)  # Add padding around the content
        content_layout.setSpacing(10)  # Add space between widgets
        
        # Terminal Emulator selection
        self.terminal_label = QLabel("Terminal Emulator:")
        content_layout.addWidget(self.terminal_label)
        
        self.terminal_combo = QComboBox()
        for name in self.main_window.controller.available_terminal_emulators.keys():
            self.terminal_combo.addItem(name)
        current_terminal = self.main_window.controller.config.get('terminal_emulator')
        index = self.terminal_combo.findText(current_terminal)
        if index >= 0:
            self.terminal_combo.setCurrentIndex(index)
        content_layout.addWidget(self.terminal_combo)
        
        # Theme selection
        self.theme_label = QLabel("Theme:")
        content_layout.addWidget(self.theme_label)
        
        self.theme_combo = QComboBox()
        themes = self.get_available_themes()
        for theme in themes:
            self.theme_combo.addItem(theme)
        current_theme = self.main_window.current_theme
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        content_layout.addWidget(self.theme_combo)
        
        # Minimize to tray option
        self.minimize_checkbox = QCheckBox("Minimize to Tray on Close")
        self.minimize_checkbox.setChecked(self.main_window.controller.get_minimize_on_close())
        content_layout.addWidget(self.minimize_checkbox)
        
        # Add some vertical spacing
        content_layout.addStretch(1)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        content_layout.addWidget(button_box)
        
        # Add the content widget to the main layout
        main_layout.addWidget(content_widget)
        
        self.setLayout(main_layout)

    def get_available_themes(self):
        return [d for d in os.listdir(THEMES_DIR) if os.path.isdir(os.path.join(THEMES_DIR, d))]

    def apply_settings(self):
        selected_terminal = self.terminal_combo.currentText()
        self.main_window.controller.set_terminal_emulator(selected_terminal)
        
        selected_theme = self.theme_combo.currentText()
        theme_data = load_theme(selected_theme)
        if theme_data:
            self.main_window.apply_theme(theme_data)
        
        minimize_on_close = self.minimize_checkbox.isChecked()
        self.main_window.controller.toggle_minimize_on_close(minimize_on_close)

    def accept(self):
        self.apply_settings()
        super().accept()

    def reject(self):
        # Close the dialog without saving any settings
        super().reject()
