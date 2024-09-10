import sys
from PyQt5.QtWidgets import QApplication
from views import MainWindow
from config import load_config, load_or_generate_key

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load configuration
    from cryptography.fernet import Fernet
    SECRET_KEY = load_or_generate_key()
    cipher_suite = Fernet(SECRET_KEY)
    config = load_config()

    # Initialize the main window
    window = MainWindow(config, cipher_suite)
    window.show()

    sys.exit(app.exec_())
