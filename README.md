# nuTTY
_A Linux only SSH Connection Manager inspired by puTTy._

**nuTTY is a work-in-progress**, designed to be a simple, user-friendly SSH connection manager for Linux, helping you keep track of your SSH connections and allows you to connect to remote servers easily using your preferred terminal emulator (if that terminal emulator is supported).

nuTTY includes a system tray icon for quick access and the ability to minimize to the tray, providing a seamless experience while managing multiple connections. **Please note that nuTTY does not package any terminal emulator**; it relies on terminal emulators already installed on your system. **Supported emulators must be available in your PATH for nuTTY to work properly**.

--------------------------------

Project Intent:

This project is not intended to be a highly polished or serious project. I primarily created it to address my own personal needs. While I'm happy to share it with others, I will only continue adding significant features and improvements if there is clear interest from the community, or if it becomes necessary to meet my own needs.

That said, I do plan to include an **AppImage** release with limited functionality in the near future, so it can be easily tested or used without needing to manually install dependencies.

## Current Limitations:

- **Identity file and password support**: Full support for identity files and password-based authentication has been implemented but not yet fully tested. As of now, nuTTY has been tested only with preexisting connections where SSH keys have already been exchanged.

- **Terminal emulator support**: Currently, only a few terminal emulators are supported. Testing has been performed with GNOME Terminal and XFCE Terminal, the other implemented terminals are just my best guesses as to what the correct arguments would be for initiating an SSH or Telnet session in the selected terminal emulator.

There are only a few terminal emulators supported and I have only tested connections with gnome-terminal and xfce4-terminal.  
<table>
<tr>
<th colspan="2">Terminal Emulators that have been implemented and **might** work</th>
</tr>
<tr><td>XTerm</td><td>Alacritty</td></tr>
<tr><td>GNOME Terminal</td><td>Kitty</td></tr>
<tr><td>Konsole</td><td>URxvt</td></tr>
<tr><td>XFCE Terminal</td><td>st</td></tr>
<tr><td>LXTerminal</td><td>Eterm</td></tr>
<tr><td>Tilix</td><td>Mate Terminal</td></tr>
</table>

## Features

- **Connection Management**: Easily add, edit, and remove onnection information so you don't loose track of the things you connect to.
- **Custom Terminal Emulators**: Choose from a variety of terminal emulators to launch your SSH sessions.
- **Connection Encryption**: All saved connection information is encrypted using `cryptography` and a key stored in the Linux `keyring` to ensure the security of your data.
- **System Tray Integration**: nuTTY can minimize to the system tray and restore when needed. Supports connecting to saved connections from the tray icon.
- **Custom Connection Settings**: Add detailed connection settings including:
  - Username
  - Hostname or IP address
  - Protocol (SSH, Telnet)
  - Port
  - Identity file
  - Password
  - X11 forwarding
  - Description for each connection
  <small>**Encrypted Storage**: Somewhat securely saves all your connection information in an encrypted file.  This stored data is only slightly more secure than your home directory, because anyone attempting to exfiltrate this file would also need to retrieve the key from the keyring.</small>
------------------------
## Screenshots

![nuTTY SSH Manager](screenshots/mainwindow.png)
![nuTTY SSH Manager](screenshots/tray.png)
------------------------
## Installation

##### **Clone the Repository**:

```bash
git clone https://github.com/mikeisfreeman/nuTTY.git
cd nutty-ssh-manager
```


##### **Create a Python Virtual Environment (Optional but Recommended)**:

```bash
python3 -m venv venv
source venv/bin/activate
```

##### **Install Dependencies**:

```bash
pip install -r requirements.txt
```

##### **Run the Application**:

```bash
python3 main.py
```
------------------------
## Usage

##### **Add a Connection**: Click on the "+" button to add a new SSH or Telnet connection. Enter the required details (username, domain/IP, protocol) and optionally configure X11 forwarding and provide a description.
##### **Connect to a Server**: Select a connection from the list and click the "Connect" button to open the terminal and start an SSH or Telnet session.
##### **System Tray**: nuTTY minimizes to the system tray. You can restore it by double-clicking the tray icon. From the tray, you can also restore or exit the app.
##### **Terminal Emulator Selection**: Use the Emulator menu to select your preferred terminal emulator for launching SSH or Telnet sessions.

## Customization

- **Custom Terminal Emulators**: You can choose from a variety of terminal emulators, such as XTerm, GNOME Terminal, Konsole, XFCE Terminal, and more. Simply go to the Emulator menu and select your preferred emulator.
- **Start on Boot**: You can set up nuTTY to start automatically on boot by adding the provided .desktop file to your system's startup applications.
- **Configuration File**: nuTTY saves your preferences in config.json and securely encrypts your saved connections in connections.dat.

## Development

If you wish to contribute or modify the application, feel free to fork the repository or submit a pull request.

## Contributing

Contributions are welcome! 


## License

nuTTY is open-source software licensed under the MIT License. See the LICENSE file for more information.


### Acknowledgments

Special thanks to all contributors and users who have or will provided feedback and suggestions to make nuTTY a better tool for managing SSH sessions.

**Author**: Mike
**Version**: 0.1.2
**Repository**: [[nuTTY](https://github.com/mikeisfreeman/nuTTY)]
