from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QHBoxLayout, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QUrl

class AddConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New SSH Connection")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Name input
        self.name_edit = QLineEdit()
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_edit)

        # Username input
        self.username_edit = QLineEdit()
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_edit)

        # Domain/IP input
        self.domain_edit = QLineEdit()
        layout.addWidget(QLabel("Domain/IP:"))
        layout.addWidget(self.domain_edit)

        # Protocol selection
        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["SSH", "Telnet"])
        layout.addWidget(QLabel("Protocol:"))
        layout.addWidget(self.protocol_select)

        # Authentication method
        self.auth_method = QCheckBox("Use Identity File (uncheck for password)")
        self.auth_method.setChecked(True)
        self.auth_method.stateChanged.connect(self.toggle_auth_method)
        layout.addWidget(self.auth_method)

        # Identity file input
        self.identity_file_layout = QHBoxLayout()
        self.identity_file_edit = QLineEdit()
        self.identity_file_button = QPushButton("Browse")
        self.identity_file_button.clicked.connect(self.browse_identity_file)
        self.identity_file_layout.addWidget(self.identity_file_edit)
        self.identity_file_layout.addWidget(self.identity_file_button)
        layout.addWidget(QLabel("Identity File:"))
        layout.addLayout(self.identity_file_layout)

        # Password input
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)

        # Initially hide password field
        self.password_label.hide()
        self.password_edit.hide()

        # X11 forwarding
        self.x11_checkbox = QCheckBox("Enable X11 Forwarding")
        layout.addWidget(self.x11_checkbox)

        # Description input
        self.description_edit = QLineEdit()
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_edit)

        # Buttons
        button_box = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(save_button)
        button_box.addWidget(cancel_button)

        layout.addLayout(button_box)

    def toggle_auth_method(self, state):
        if state == Qt.Checked:
            self.identity_file_edit.show()
            self.identity_file_button.show()
            self.password_label.hide()
            self.password_edit.hide()
        else:
            self.identity_file_edit.hide()
            self.identity_file_button.hide()
            self.password_label.show()
            self.password_edit.show()

    def browse_identity_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Identity File", "", "All Files (*)")
        if file_name:
            self.identity_file_edit.setText(file_name)

    def get_connection_details(self):
        return {
            'name': self.name_edit.text(),
            'username': self.username_edit.text(),
            'domain': self.domain_edit.text(),
            'protocol': self.protocol_select.currentText(),
            'x11': self.x11_checkbox.isChecked(),
            'description': self.description_edit.text(),
            'use_identity_file': self.auth_method.isChecked(),
            'identity_file': self.identity_file_edit.text() if self.auth_method.isChecked() else None,
            'password': self.password_edit.text() if not self.auth_method.isChecked() else None
        }


class EditConnectionDialog(AddConnectionDialog):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Connection")
        
        if connection:
            self.name_edit.setText(connection.get('name', ''))
            self.username_edit.setText(connection.get('username', ''))
            self.domain_edit.setText(connection.get('domain', ''))
            self.protocol_select.setCurrentText(connection.get('protocol', 'SSH'))
            self.x11_checkbox.setChecked(connection.get('x11', False))
            self.description_edit.setText(connection.get('description', ''))
            self.auth_method.setChecked(connection.get('use_identity_file', True))
            self.identity_file_edit.setText(connection.get('identity_file', ''))
            self.password_edit.setText(connection.get('password', ''))
            
            # Manually call toggle_auth_method to ensure correct visibility of fields
            self.toggle_auth_method(self.auth_method.checkState())
            
            # Connect protocol selection to update UI
            self.protocol_select.currentTextChanged.connect(self.update_ui_for_protocol)
            self.update_ui_for_protocol(connection.get('protocol', 'SSH'))

    def update_ui_for_protocol(self, protocol):
        if protocol == 'Telnet':
            self.auth_method.setEnabled(False)
            self.x11_checkbox.setEnabled(False)
            self.identity_file_edit.setEnabled(False)
            self.identity_file_button.setEnabled(False)
        else:
            self.auth_method.setEnabled(True)
            self.x11_checkbox.setEnabled(True)
            self.identity_file_edit.setEnabled(self.auth_method.isChecked())
            self.identity_file_button.setEnabled(self.auth_method.isChecked())

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About nuTTY")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Create a horizontal layout for the image and text
        content_layout = QHBoxLayout()

        # Set the text for the about message
        text_label = QLabel(
            "nuTTY is a simple, user-friendly SSH and Telnet session manager.\n"
            "Created to manage your connections with ease.\n\n"
            "Version: 0.3.0\n"
            "Author: Mike\n"
        )
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Create a single label for both links
        links_label = QLabel(
            "View nuTTY on <a href='https://github.com/mikeisfreeman/nuTTY'>GitHub</a><br>"
            "<a href='https://github.com/mikeisfreeman/nuTTY/#'>Check for Updates</a>"
        )
        links_label.setOpenExternalLinks(True)
        links_label.setTextFormat(Qt.RichText)
        links_label.setTextInteractionFlags(Qt.TextBrowserInteraction)

        # Create a vertical layout for text and links
        text_layout = QVBoxLayout()
        text_layout.addWidget(text_label)
        text_layout.addWidget(links_label)
        text_layout.setSpacing(0)  # Reduce spacing between widgets

        # Set an icon next to the text
        custom_image = QLabel()
        custom_image.setPixmap(QPixmap("assets/icons/nuTTY_256x256_about.png"))

        # Add image and text to the horizontal layout
        content_layout.addWidget(custom_image)
        content_layout.addLayout(text_layout)

        # Add the content layout to the main layout
        layout.addLayout(content_layout)

        # Add a close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignHCenter)

