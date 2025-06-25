# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from db import DBManager
import config
from sqlalchemy import text


class SubAPUEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sub APU")
        self.setMinimumSize(900, 500)

        layout = QVBoxLayout()
        self.label = QLabel(f"SubAPU de la Subpartida: {config.codigo_subpartida_actual}")
        layout.addWidget(self.label)

        self.table = QTableView()
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID",
            "Código",
            "Recurso",
            "Tipo",
            "Unidad",
            "Cuadrilla",
            "Rendimiento",
            "Cantidad",
            "Precio",
            "Parcial",
        ])
        self.table.setModel(self.model)

        self.cargar_sub_apu()

    def cargar_sub_apu(self):
        db = DBManager()
        self.model.removeRows(0, self.model.rowCount())

        query = (
            "SELECT id_sub_apu, codigo_recurso, recurso_name, tipo, unidad, "
            "cuadrilla, rendimiento, cantidad, precio, parcial "
            "FROM sub_apu_programado WHERE codigo_subpartida = :codigo ORDER BY id_sub_apu"
        )

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text(query), {"codigo": config.codigo_subpartida_actual})
                for row in result:
                    items = []
                    for val in row:
                        if isinstance(val, bytes):
                            try:
                                val = val.decode("latin1")
                            except Exception:
                                val = "??"
                        items.append(QStandardItem(str(val)))
                    self.model.appendRow(items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos del Sub APU:\n{e}")

