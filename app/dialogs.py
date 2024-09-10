from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap

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

    def get_connection_details(self):
        return {
            'name': self.name_edit.text(),
            'username': self.username_edit.text(),
            'domain': self.domain_edit.text(),
            'protocol': self.protocol_select.currentText(),
            'x11': self.x11_checkbox.isChecked(),
            'description': self.description_edit.text()
        }


class AboutDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About nuTTY")
        self.setModal(True)
        # Set the text for the about message
        self.setText("nuTTY is a simple, user-friendly SSH and Telnet session manager.\n"
                            "Created to manage your connections with ease.\n\n"
                            "Version: 0.1.5.2\nAuthor: Mike")
        
        # Set an icon next to the text in the QMessageBox
        custom_image = QLabel()
        custom_image.setPixmap(QPixmap("assets/icons/nuTTY_256x256_about.png"))

        # Insert image into the message box
        self.layout().addWidget(custom_image, 0, self.layout().rowCount(), 1, -1)
        

# Create a custom QMessageBox instance
# about_dialog = QMessageBox(self)
# about_dialog.setWindowTitle("About nuTTY")

# about_dialog.setIconPixmap(QPixmap())  # Clear the default icon

# # Set the text for the about message
# about_dialog.setText("nuTTY is a simple, user-friendly SSH and Telnet session manager.\n"
#                     "Created to manage your connections with ease.\n\n"
#                     "Version: 0.1.5.2\nAuthor: Mike")

# # Set an icon next to the text in the QMessageBox
# custom_image = QLabel()
# custom_image.setPixmap(QPixmap("assets/icons/nuTTY_256x256_about.png"))

# # Insert image into the message box
# about_dialog.layout().addWidget(custom_image, 0, about_dialog.layout().rowCount(), 1, -1)

# # Show the about dialog
# about_dialog.exec_()
