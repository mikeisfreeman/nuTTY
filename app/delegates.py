from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QFont, QPen, QColor
from PyQt5.QtCore import QRect, Qt, QSize

from PyQt5.QtCore import Qt


class ConnectionItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Get the connection details from the model (now it returns a dictionary)
        connection = index.data(Qt.DisplayRole)
        if not connection:
            return
        
        painter.save()

        # Extract the connection fields
        name = connection.get('name', 'Unknown Name')
        username = connection.get('username', 'Unknown User')
        domain = connection.get('domain', 'Unknown Domain')
        description = connection.get('description', 'No description')

        # Check if the item is selected
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, QColor("#f9f9f9"))  # Light gray background for unselected

        # Define padding and spacing
        padding = 5
        name_font_size = 12
        domain_font_size = 11
        description_font_size = 10

        # Define rectangles for name, username, domain (IP), and description
        name_rect = QRect(option.rect.left() + padding, option.rect.top() + padding, option.rect.width() - padding * 2, option.rect.height() // 4 - padding)
        domain_rect = QRect(option.rect.left() + padding, option.rect.top() + option.rect.height() // 4, option.rect.width() - padding * 2, option.rect.height() // 4 - padding)
        description_rect = QRect(option.rect.left() + padding, option.rect.top() + 2 * (option.rect.height() // 4), option.rect.width() - padding * 2, option.rect.height() // 4 - padding)

        # Customize fonts
        name_font = QFont()
        name_font.setPointSize(name_font_size)
        name_font.setBold(True)

        domain_font = QFont()
        domain_font.setPointSize(domain_font_size)

        description_font = QFont()
        description_font.setPointSize(description_font_size)
        description_font.setItalic(True)

        # Set up pen for text color
        name_pen = QPen(QColor("#333333"))  # Dark text color for name
        domain_pen = QPen(QColor("#555555"))  # Medium gray for domain (IP)
        description_pen = QPen(QColor("#777777"))  # Lighter gray for description

        # Draw the connection name (in bold)
        painter.setFont(name_font)
        painter.setPen(name_pen)
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, f"{name} ({username})")

        # Draw the domain (IP address)
        painter.setFont(domain_font)
        painter.setPen(domain_pen)
        painter.drawText(domain_rect, Qt.AlignLeft | Qt.AlignVCenter, f"Domain/IP: {domain}")

        # Draw the connection description (in italic)
        painter.setFont(description_font)
        painter.setPen(description_pen)
        painter.drawText(description_rect, Qt.AlignLeft | Qt.AlignVCenter, description)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(200, 80)  # Adjusted height to fit name, domain, and description

    