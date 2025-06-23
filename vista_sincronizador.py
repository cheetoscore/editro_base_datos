from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QMessageBox,
    QComboBox,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from sincronizador import sincronizar, obtener_tablas
import subprocess
import os


def crear_sincronizador_ui():
    ventana = QWidget()
    ventana.setWindowTitle("📡 Sincronización de Base de Datos")
    ventana.setGeometry(300, 200, 600, 550)

    layout = QVBoxLayout()

    label_info = QLabel("Selecciona las tablas a sincronizar:")
    layout.addWidget(label_info)

    lista_tablas = QListWidget()
    lista_tablas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout.addWidget(lista_tablas)

    combo_direccion = QComboBox()
    combo_direccion.addItem("⬆️ Local ➜ Online", userData="local_a_online")
    combo_direccion.addItem("⬇️ Online ➜ Local", userData="online_a_local")

    layout.addWidget(QLabel("Dirección de sincronización:"))
    layout.addWidget(combo_direccion)

    def cargar_tablas_dinamicamente():
        direccion = combo_direccion.currentData()
        origen = "local" if direccion == "local_a_online" else "online"
        lista_tablas.clear()
        try:
            tablas = obtener_tablas(direccion=origen)
            for tabla in tablas:
                item = QListWidgetItem()
                checkbox = QCheckBox(tabla)
                lista_tablas.addItem(item)
                lista_tablas.setItemWidget(item, checkbox)
        except Exception as e:
            QMessageBox.critical(ventana, "Error", f"No se pudieron cargar las tablas:\n{str(e)}")

    combo_direccion.currentIndexChanged.connect(cargar_tablas_dinamicamente)

    boton_sincronizar = QPushButton("🔁 Sincronizar")
    layout.addWidget(boton_sincronizar)

    boton_backup = QPushButton("📦 Hacer Backup Local")
    layout.addWidget(boton_backup)

    def ejecutar_backup_local():
        try:
            pg_bin = os.getenv("PG_DUMP_PATH", "pg_dump")
            archivo_backup = os.path.expanduser("~/.backup_jergo_db.backup")
            comando = [
                pg_bin,
                "-U",
                "postgres",
                "-F",
                "c",
                "-f",
                archivo_backup,
                "jergo_local",
            ]
            resultado = subprocess.run(comando, env={"PGPASSWORD": os.getenv("PGPASSWORD", "")}, capture_output=True, text=True)

            if resultado.returncode == 0:
                QMessageBox.information(ventana, "Backup exitoso", f"Backup creado en:\n{archivo_backup}")
            else:
                raise Exception(resultado.stderr)
        except Exception as e:
            QMessageBox.critical(ventana, "Error en backup", f"No se pudo crear el backup:\n{str(e)}")

    def ejecutar_sincronizacion():
        tablas_seleccionadas = []
        for i in range(lista_tablas.count()):
            item = lista_tablas.item(i)
            widget = lista_tablas.itemWidget(item)
            if widget.isChecked():
                tablas_seleccionadas.append(widget.text())

        if not tablas_seleccionadas:
            QMessageBox.warning(ventana, "Advertencia", "Selecciona al menos una tabla.")
            return

        direccion = combo_direccion.currentData()
        confirmacion = QMessageBox.question(
            ventana,
            "Confirmar sincronización",
            f"¿Estás seguro de sincronizar {len(tablas_seleccionadas)} tabla(s) en dirección:\n{combo_direccion.currentText()}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirmacion == QMessageBox.Yes:
            sincronizar(tablas_seleccionadas, direccion)
            QMessageBox.information(ventana, "Completado", "Sincronización finalizada.")

    boton_sincronizar.clicked.connect(ejecutar_sincronizacion)
    boton_backup.clicked.connect(ejecutar_backup_local)
    ventana.setLayout(layout)

    cargar_tablas_dinamicamente()

    return ventana

