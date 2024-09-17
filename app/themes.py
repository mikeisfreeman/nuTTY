from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout

class ThemeDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Select Theme")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Theme list
        self.theme_list = QListWidget()
        self.theme_list.addItems(self.config.get_available_themes())
        layout.addWidget(self.theme_list)

        # Buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_theme)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(apply_button)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def apply_theme(self):
        selected_items = self.theme_list.selectedItems()
        if selected_items:
            selected_theme = selected_items[0].text()
            theme_data = self.config.load_theme(selected_theme)
            if theme_data:
                self.parent().apply_theme(theme_data)
        # Note: We don't call self.accept() here, so the dialog stays open
        print("Theme data:", theme_data)

    def accept(self):
        # Apply the theme one last time before closing the dialog
        self.apply_theme()
        super().accept()
