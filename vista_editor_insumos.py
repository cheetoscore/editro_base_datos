from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QMessageBox
from modelo_tabla import PandasModel
from guardar import guardar_dataframe
from db import DBManager
import pandas as pd
import config
from sqlalchemy import text
from PyQt5.QtGui import QColor

def crear_editor_insumos(id_partida_destacada=None):
    from PyQt5.QtGui import QColor
    ventana = QWidget()
    ventana.setWindowTitle("Editor de Insumos Programados")
    layout = QVBoxLayout()

    tabla = QTableView()
    layout.addWidget(tabla)

    db = DBManager()

    # Paso 1: obtener recursos APU de la partida (por nombre)
    recursos_partida = set()
    if id_partida_destacada:
        try:
            query_apu = f"""
                SELECT recurso_name FROM apu_programado
                WHERE id_partida = {id_partida_destacada}
            """
            df_apu = db.obtener_dataframe(query_apu)
            recursos_partida = set(df_apu["recurso_name"].astype(str).str.strip())
        except Exception as e:
            print(f"❌ Error al buscar insumos APU: {e}")

    # Paso 2: cargar listado de insumos del proyecto
    try:
        df = db.obtener_dataframe(f"""
            SELECT * FROM listado_insumos_programados
            WHERE id_proyecto = {config.id_proyecto_actual}
            ORDER BY recurso_name
        """)
    except Exception as e:
        QMessageBox.critical(ventana, "Error", f"No se pudo cargar la tabla de insumos:\n{e}")
        df = pd.DataFrame()

    # Paso 3: cargar modelo con estilos
    modelo = PandasModel(df)

    # Aplicar estilos a los recursos que pertenecen al APU de la partida
    if not df.empty and recursos_partida:
        for i in range(df.shape[0]):
            nombre_insumo = str(df.loc[i, "recurso_name"]).strip()
            if nombre_insumo in recursos_partida:
                for j in range(df.shape[1]):
                    modelo._data_styles[(i, j)] = {"background": QColor("#FFFACD")}  # amarillo claro

    tabla.setModel(modelo)

    boton_guardar = QPushButton("Guardar Cambios")
    layout.addWidget(boton_guardar)

    def guardar():
        df_editado = modelo._data
        guardar_dataframe(df_editado, "listado_insumos_programados")
        QMessageBox.information(ventana, "Guardado", "✅ Insumos guardados correctamente.")

    boton_guardar.clicked.connect(guardar)

    ventana.setLayout(layout)
    return ventana
