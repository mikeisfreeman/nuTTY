from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def setup_tray_icon(parent):
    tray_icon = QSystemTrayIcon(QIcon("assets/icons/nuTTY_64x64_dark.png"), parent)
    tray_icon.setToolTip("nuTTY SSH Manager")

    # Tray menu
    tray_menu = QMenu()

    # Add dynamic list of connections
    parent.update_tray_connections(tray_menu)

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

