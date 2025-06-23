from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView, QMessageBox, QPushButton, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from sqlalchemy import text
from db import DBManager
import config
from vista_editor_sub_apu import SubAPUEditor
from vista_editor_insumos import crear_editor_insumos
from logica_apus import recalcular_apu, guardar_apu, limpiar_filas_subtotales

class EditorAPUs(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 500)

        layout = QVBoxLayout()

        self.label = QLabel()
        layout.addWidget(self.label)

        self.table = QTableView()
        layout.addWidget(self.table)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "ID Recurso", "Recurso", "Tipo", "Unidad",
            "Cuadrilla", "Rendimiento", "Cantidad", "Precio", "Parcial"
        ])
        self.table.setModel(self.model)

        botones_layout = QHBoxLayout()

        self.btn_ver_sub_apu = QPushButton("📄 Ver SubAPU")
        self.btn_ver_sub_apu.clicked.connect(self.ver_sub_apu)
        botones_layout.addWidget(self.btn_ver_sub_apu)

        self.btn_ver_insumos = QPushButton("📋 Ver Insumos")
        self.btn_ver_insumos.clicked.connect(self.ver_insumos)
        botones_layout.addWidget(self.btn_ver_insumos)

        self.btn_recalcular = QPushButton("🔄 Recalcular APU")
        self.btn_recalcular.clicked.connect(lambda: self.recalcular_y_ajustar())
        botones_layout.addWidget(self.btn_recalcular)

        self.btn_guardar = QPushButton("💾 Guardar APU")
        self.btn_guardar.clicked.connect(self.guardar_y_recargar)
        botones_layout.addWidget(self.btn_guardar)

        self.btn_agregar = QPushButton("➕ Agregar Fila")
        self.btn_agregar.clicked.connect(self.agregar_fila)
        botones_layout.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("❌ Eliminar Fila")
        self.btn_eliminar.clicked.connect(self.eliminar_fila)
        botones_layout.addWidget(self.btn_eliminar)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

        self.cargar_apus()

    def cargar_apus(self):
        db = DBManager()
        self.model.removeRows(0, self.model.rowCount())

        query = f"""
            SELECT id, id_recurso, recurso_name, tipo, unidad,
                   cuadrilla, rendimiento, cantidad, precio, parcial,
                   codigo_partida, partida_name
            FROM apu_programado
            WHERE id_partida = {config.id_partida_actual}
            ORDER BY id
        """

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()

                if not rows:
                    self.setWindowTitle("APU - Sin datos")
                    self.label.setText("No hay datos APU para esta partida.")
                    return

                cod_partida = rows[0][-2]
                nombre_partida = rows[0][-1]
                self.setWindowTitle(f"APU - {cod_partida} - {nombre_partida}")
                self.label.setText(f"Partida: {cod_partida} - {nombre_partida}")

                for row in rows:
                    items = []
                    for val in row[:-2]:
                        val = val.decode("latin1") if isinstance(val, bytes) else val
                        items.append(QStandardItem(str(val)))
                    self.model.appendRow(items)

                self.table.setColumnHidden(0, True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los APUs:\n{e}")

    def ver_sub_apu(self):
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Advertencia", "Seleccione un recurso.")
            return

        tipo = self.model.item(index.row(), 3).text().strip().upper()
        if tipo != "SUB-PARTIDA":
            QMessageBox.information(self, "Info", "Este recurso no es una SUB-PARTIDA.")
            return

        codigo_recurso = self.model.item(index.row(), 1).text()
        config.codigo_subpartida_actual = codigo_recurso
        self.ventana_subapu = SubAPUEditor()
        self.ventana_subapu.show()

    def ver_insumos(self):
        self.ventana_insumos = crear_editor_insumos(id_partida_destacada=config.id_partida_actual)
        self.ventana_insumos.show()

    def agregar_fila(self):
        nueva = [
            QStandardItem("Nuevo"), QStandardItem(""), QStandardItem(""),
            QStandardItem("MANO DE OBRA"), QStandardItem(""),
            QStandardItem("0"), QStandardItem("0"), QStandardItem("0"),
            QStandardItem("0"), QStandardItem("0")
        ]
        self.model.appendRow(nueva)

    def eliminar_fila(self):
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Advertencia", "Seleccione una fila para eliminar.")
            return

        fila = index.row()
        id_val = self.model.item(fila, 0).text()
        confirmar = QMessageBox.question(self, "Confirmar", f"¿Eliminar fila con ID {id_val}?", QMessageBox.Yes | QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            if id_val.lower() != "nuevo":
                db = DBManager()
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text("DELETE FROM apu_programado WHERE id = :id"), {"id": int(id_val)})
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")
                    return
            self.model.removeRow(fila)

    def guardar_y_recargar(self):
        guardar_apu(self.model)
        self.cargar_apus()

    def recalcular_y_ajustar(self):
        limpiar_filas_subtotales(self.model)
        recalcular_apu(self.model)

def crear_editor_apus():
    return EditorAPUs()
