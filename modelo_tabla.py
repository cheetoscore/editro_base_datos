from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt5.QtGui import QColor

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super(PandasModel, self).__init__()
        self._data = data.copy()
        self._data_styles = {}  # clave: (row, col), valor: {"background": QColor(...)} opcional

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, col = index.row(), index.column()
        value = self._data.iloc[row, col]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(value)

        # Color de fondo
        if role == Qt.BackgroundRole:
            style = self._data_styles.get((row, col))
            if style and "background" in style:
                return style["background"]

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            row, col = index.row(), index.column()
            try:
                # Conversión numérica si corresponde
                colname = self._data.columns[col]
                if self._data[colname].dtype.kind in 'if':
                    value = float(value)
                self._data.iloc[row, col] = value
                self.dataChanged.emit(index, index)
                return True
            except Exception as e:
                print(f"⚠️ Error al editar valor: {e}")
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            if orientation == Qt.Vertical:
                return section + 1
        return QVariant()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
