from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def setup_tray_icon(parent, connection_model):
    tray_icon = QSystemTrayIcon(QIcon("assets/icons/nuTTY_64x64_dark.png"), parent)
    tray_icon.setToolTip("nuTTY SSH Manager")

    # Tray menu
    tray_menu = QMenu()

    # Add dynamic list of connections
    update_tray_connections(tray_menu, connection_model, parent)

    # Restore action
    restore_action = QAction("Restore", parent)
    restore_action.triggered.connect(parent.show)
    tray_menu.addAction(restore_action)
    
    # Exit action
    exit_action = QAction("Exit", parent)
    exit_action.triggered.connect(parent.exit_app)
    tray_menu.addAction(exit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.activated.connect(parent.tray_icon_activated)
    tray_icon.show()

    return tray_icon

def update_tray_connections(tray_menu, connection_model, parent):
    """Dynamically populate the tray menu with a list of connections."""
    # Clear any existing connections to avoid duplicates
    tray_menu.clear()

    # Add a section for the connections
    connections_menu = QMenu("Connections", parent)

    # Loop through the model and add each connection as an action in the tray menu
    for row in range(connection_model.rowCount()):
        connection = connection_model.get_connection(row)

        connection_action = QAction(f"{connection['name']} - {connection['domain']}", parent)
        connection_action.triggered.connect(lambda checked, row=row: parent.connect_to_server_from_tray(row))
        connections_menu.addAction(connection_action)

    # Add the connections menu to the tray menu
    tray_menu.addMenu(connections_menu)

