from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from sqlalchemy import text
from db import DBManager


class EditorProyectos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Proyectos")
        self.setMinimumSize(800, 400)

        layout = QVBoxLayout()

        self.btn_cargar = QPushButton("🔄 Cargar Proyectos")
        self.btn_cargar.clicked.connect(self.cargar_proyectos)
        layout.addWidget(self.btn_cargar)

        self.table = QTableView()
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Nombre del Proyecto", "Cliente", "Ubicación"
        ])
        self.table.setModel(self.model)

        self.cargar_proyectos()

    def cargar_proyectos(self):
        db = DBManager()
        self.model.removeRows(0, self.model.rowCount())
        try:
            query = """
                SELECT id_proyecto, proyecto_name, cliente, ubicacion
                FROM proyectos ORDER BY id_proyecto
            """
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                for row in result:
                    items = []
                    for valor in row:
                        if isinstance(valor, bytes):
                            try:
                                valor = valor.decode('latin1')
                            except:
                                valor = "??"
                        items.append(QStandardItem(str(valor)))
                    self.model.appendRow(items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla de proyectos:\n{e}")


def crear_editor_proyectos():
    return EditorProyectos()
