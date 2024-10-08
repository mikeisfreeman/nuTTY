from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal

class TrayManager(QObject):
    connect_to_server_signal = pyqtSignal(int)
    show_window_signal = pyqtSignal()
    exit_app_signal = pyqtSignal()

    def __init__(self, parent, connection_model):
        super().__init__(parent)
        self.parent = parent
        self.connection_model = connection_model
        self.tray_icon = self.setup_tray_icon()

    def setup_tray_icon(self):
        tray_icon = QSystemTrayIcon(QIcon("assets/icons/nuTTY_64x64_dark.png"), self.parent)
        tray_icon.setToolTip("nuTTY SSH Manager")

        # Create the tray menu
        tray_menu = QMenu()
        
        # Add dynamic list of connections
        self.connections_menu = QMenu("Connections", self.parent)
        tray_menu.addMenu(self.connections_menu)
        
        # Add separator
        tray_menu.addSeparator()

        # Restore action
        restore_action = QAction("Restore", self.parent)
        restore_action.triggered.connect(self.show_window_signal.emit)
        tray_menu.addAction(restore_action)
        
        # Exit action
        exit_action = QAction("Exit", self.parent)
        exit_action.triggered.connect(self.exit_app_signal.emit)
        tray_menu.addAction(exit_action)

        tray_icon.setContextMenu(tray_menu)
        tray_icon.activated.connect(self.tray_icon_activated)
        tray_icon.show()

        # Initial update of connections
        self.update_tray_connections()

        return tray_icon

    def update_tray_connections(self):
        """Dynamically populate the connections submenu with a list of connections."""
        self.connections_menu.clear()

        # Loop through the model and add each connection as an action in the connections submenu
        for row in range(self.connection_model.rowCount()):
            connection = self.connection_model.get_connection(row)

            connection_action = QAction(f"{connection['name']} - {connection['domain']}", self.parent)
            connection_action.triggered.connect(lambda checked, row=row: self.connect_to_server_signal.emit(row))
            self.connections_menu.addAction(connection_action)

    def tray_icon_activated(self, reason):
        """Handle tray icon click."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window_signal.emit()

    def show_message(self, title, message, icon=QSystemTrayIcon.Information, duration=2000):
        """Show a tray icon message."""
        self.tray_icon.showMessage(title, message, icon, duration)

    def hide_tray_icon(self):
        """Hide the tray icon."""
        self.tray_icon.hide()

def create_tray_manager(parent, connection_model):
    return TrayManager(parent, connection_model)

