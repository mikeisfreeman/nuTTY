import logging
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
from PyQt5.QtGui import QFont, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QRect, QSize

class ConnectionItemDelegate(QStyledItemDelegate):
    def __init__(self, theme_data):
        super().__init__()
        self.theme_data = theme_data
        self.logger = logging.getLogger(__name__)

    def paint(self, painter, option, index):
        connection = index.data(Qt.DisplayRole)
        if not connection:
            return
        
        painter.save()

        # Parse colors with alpha
        bg_color = self.parse_color(self.theme_data.get('list_view_item_background-color', 'rgba(255, 255, 255, 255)'))
        selected_bg_color = self.parse_color(self.theme_data.get('list_view_item_selected_background-color', 'rgba(230, 243, 255, 255)'))
        border_color = self.parse_color(self.theme_data.get('list_view_border', '#d0d0d0').split()[2])
        
        name_color = self.parse_color(self.theme_data.get('list_view_item_name_color', '#000000'))
        info_color = self.parse_color(self.theme_data.get('list_view_item_info_color', name_color.lighter(130).name()))
        desc_color = self.parse_color(self.theme_data.get('list_view_item_desc_color', name_color.lighter(150).name()))
        
        selected_name_color = self.parse_color(self.theme_data.get('list_view_item_selected_name_color', '#000000'))
        selected_info_color = self.parse_color(self.theme_data.get('list_view_item_selected_info_color', '#000000'))
        selected_desc_color = self.parse_color(self.theme_data.get('list_view_item_selected_description_color', '#000000'))
        
        
        # Draw background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QBrush(selected_bg_color))
        else:
            painter.fillRect(option.rect, QBrush(bg_color))

        # Draw border
        painter.setPen(QPen(border_color))
        painter.drawRect(option.rect)

        name = connection.get('name', 'Unknown Name')
        host = connection.get('domain', 'Unknown Host')
        username = connection.get('username', 'Unknown Username')
        connection_info = f"{username}@{host}"
        description = connection.get('description', "")

        # Set fonts colors
        if option.state & QStyle.State_Selected:
            name_draw_color = selected_name_color
            info_draw_color = selected_info_color
            desc_draw_color = selected_desc_color
        else:
            name_draw_color = name_color
            info_draw_color = info_color
            desc_draw_color = desc_color
            
        font_family = self.theme_data.get('list_view_font-family', 'Arial, sans-serif').replace("'", "")
        name_font = QFont(font_family, 12, QFont.Bold)
        info_font = QFont(font_family, 10)
        description_font = QFont(font_family, 8)

        # Calculate text rectangles
        name_rect = QRect(option.rect.left() + 10, option.rect.top() + 10, option.rect.width() - 20, 20)
        info_rect = QRect(option.rect.left() + 10, name_rect.bottom() + 5, option.rect.width() - 20, 20)
        description_rect = QRect(option.rect.left() + 10, info_rect.bottom() + 5, option.rect.width() - 20, 20)

        # Draw name
        painter.setFont(name_font)
        painter.setPen(QPen(name_draw_color))
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, name)

        # Draw connection info
        painter.setFont(info_font)
        painter.setPen(QPen(info_draw_color))
        painter.drawText(info_rect, Qt.AlignLeft | Qt.AlignVCenter, connection_info)

        # Draw description
        painter.setFont(description_font)
        painter.setPen(QPen(desc_draw_color))
        painter.drawText(description_rect, Qt.AlignLeft | Qt.AlignVCenter, description)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(200, 100)

    def parse_color(self, color_string):
        if color_string.startswith('rgba'):
            r, g, b, a = map(int, color_string.strip('rgba()').split(','))
            return QColor(r, g, b, a)
        elif color_string.startswith('#'):
            return QColor(color_string)
        else:
            return QColor(color_string)

