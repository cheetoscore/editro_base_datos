from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from sqlalchemy import text
from db import DBManager, decodificar
import config

class SelectorProyectoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar Proyecto")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Seleccione el proyecto con el que desea trabajar:"))

        self.combo = QComboBox()
        layout.addWidget(self.combo)

        self.btn_aceptar = QPushButton("✅ Aceptar")
        self.btn_aceptar.clicked.connect(self.seleccionar_proyecto)
        layout.addWidget(self.btn_aceptar)

        self.setLayout(layout)
        self.cargar_proyectos()

    def cargar_proyectos(self):
        db = DBManager()
        try:
            query = """
                SELECT id_proyecto, proyecto_name
                FROM proyectos
                ORDER BY id_proyecto
            """
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                for row in result:
                    id_proyecto = row[0]
                    nombre = row[1]
                    if isinstance(nombre, bytes):
                        nombre = decodificar(nombre)
                    texto = f"{id_proyecto} - {nombre}"
                    self.combo.addItem(texto, id_proyecto)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los proyectos:\n{e}")
            self.reject()

    def seleccionar_proyecto(self):
        index = self.combo.currentIndex()
        id_proyecto = self.combo.itemData(index)
        nombre_visible = self.combo.currentText()

        if id_proyecto is None:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un proyecto válido.")
            return

        config.id_proyecto_actual = id_proyecto
        config.nombre_proyecto_actual = nombre_visible

        self.accept()
