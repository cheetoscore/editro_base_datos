from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from sqlalchemy import text
from db import DBManager
import config
from filtros import cargar_tipo_partidas
from vista_editor_apus import crear_editor_apus

class EditorPartidas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Partidas")
        self.setMinimumSize(1000, 500)

        layout = QVBoxLayout()

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Filtrar por tipo de partida:"))

        self.combo_tipo_partida = QComboBox()
        filtro_layout.addWidget(self.combo_tipo_partida)

        self.btn_filtrar = QPushButton("🔍 Filtrar")
        self.btn_filtrar.clicked.connect(self.cargar_partidas)
        filtro_layout.addWidget(self.btn_filtrar)

        self.btn_ver_apu = QPushButton("📄 Ver APU")
        self.btn_ver_apu.clicked.connect(self.ver_apu)
        filtro_layout.addWidget(self.btn_ver_apu)

        layout.addLayout(filtro_layout)

        self.table = QTableView()
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Unidad", "Cantidad",
            "Subtotal", "P.U Oferta", "G.G", "Utilidad", "Total"
        ])
        self.table.setModel(self.model)

        cargar_tipo_partidas(self.combo_tipo_partida, config.id_proyecto_actual)
        self.cargar_partidas()

    def cargar_partidas(self):
        db = DBManager()
        self.model.removeRows(0, self.model.rowCount())
        tipo_filtro = self.combo_tipo_partida.currentText()

        # Aplicar filtro solo si no es "Todos"
        condicion_filtro = ""
        if tipo_filtro and tipo_filtro.strip().lower() != "todos":
            condicion_filtro = f"AND tipo_partida = '{tipo_filtro}'"

        query = f"""
            SELECT id_partida, codigo_partida, partida_name, unidad, cantidad,
                   subtotal, p_u_oferta, gg, utilidad, total
            FROM partidas
            WHERE id_proyecto = {config.id_proyecto_actual}
            {condicion_filtro}
            ORDER BY id_partida
        """

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                for row in result:
                    items = []
                    for val in row:
                        if isinstance(val, bytes):
                            try:
                                val = val.decode("latin1")
                            except:
                                val = "??"
                        items.append(QStandardItem(str(val)))
                    self.model.appendRow(items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las partidas:\n{e}")

    def ver_apu(self):
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar una partida.")
            return
        id_partida = int(self.model.item(index.row(), 0).text())
        config.id_partida_actual = id_partida
        self.ventana_apu = crear_editor_apus()
        self.ventana_apu.show()


def crear_editor_partidas():
    return EditorPartidas()
