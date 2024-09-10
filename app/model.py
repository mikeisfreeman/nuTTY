from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex

class ConnectionListModel(QAbstractListModel):
    def __init__(self, connections=None):
        super().__init__()
        # Initialize the connections list, defaulting to an empty list if none provided
        self.connections = connections or []
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Return the full connection dictionary instead of a formatted string
            return self.connections[index.row()]

    def rowCount(self, index=QModelIndex()):
        return len(self.connections)

    def add_connection(self, connection):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.connections.append(connection)
        self.endInsertRows()

    def remove_connection(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        del self.connections[index]
        self.endRemoveRows()

    def get_connection(self, row):
        return self.connections[row]
