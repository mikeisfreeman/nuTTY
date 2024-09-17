# nuTTY SSH Manager

nuTTY is a simple, user-friendly SSH and Telnet session manager for Linux. It helps you manage your SSH and Telnet connections and allows you to connect to remote servers easily using your preferred terminal emulator.

nuTTY includes a system tray icon for quick access and the ability to minimize to the tray, providing a seamless experience while managing multiple connections. **Please note that nuTTY does not package any terminal emulator**; it relies on terminal emulators already installed on your system. **Supported emulators must be available in your PATH for nuTTY to work properly**.

## Features

- **SSH and Telnet Session Management**: Easily add, edit, remove, and duplicate SSH and Telnet connections.
- **Multiple Authentication Methods**: Support for both password and identity file authentication for SSH connections.
- **Custom Terminal Emulators**: Choose from a variety of terminal emulators to launch your SSH sessions.
- **Connection Encryption**: All saved connections are encrypted using `cryptography` to ensure the security of your data.
- **System Tray Integration**: nuTTY can minimize to the system tray and restore when needed. Supports double-click activation from the tray icon.
- **X11 Forwarding**: Support for X11 forwarding in SSH connections.
- **Themes**: Multiple built-in themes available (coffee, monokai, oceanic, light, dark, matrix, nord, gruvbox).
- **Custom Connection Settings**: Add detailed connection settings including:
  - Username
  - Hostname or IP address
  - Protocol (SSH, Telnet)
  - X11 forwarding
  - Description for each connection

## Current Limitations

- **Telnet support**: While implemented, Telnet support is not fully tested yet.

## Supported Terminal Emulators

nuTTY supports various terminal emulators. The following have been implemented and should work:

- XTerm
- GNOME Terminal
- Konsole
- XFCE Terminal
- LXTerminal
- Tilix
- Alacritty
- Kitty
- URxvt
- st
- Eterm
- Mate Terminal

## Installation

1. **Clone the Repository**:
