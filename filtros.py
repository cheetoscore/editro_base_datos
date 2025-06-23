import pandas as pd
from db import DBManager

def cargar_id_proyectos(combo):
    """Llena un QComboBox con id_proyecto + nombre del proyecto."""
    combo.clear()
    combo.addItem("Todos", "Todos")  # valor visible y clave interna

    query = """
        SELECT DISTINCT p.id_proyecto, pr.proyecto_name
        FROM partidas p
        JOIN proyectos pr ON p.id_proyecto = pr.id_proyecto
        ORDER BY p.id_proyecto
    """

    db = DBManager()
    try:
        df = db.obtener_dataframe(query)
        for _, row in df.iterrows():
            texto = f"{row['id_proyecto']} - {row['proyecto_name']}"
            combo.addItem(texto, row['id_proyecto'])  # texto visible, valor interno
    except Exception as e:
        print(f"❌ Error al cargar proyectos: {e}")

def cargar_tipo_partidas(combo, id_proyecto=None):
    """Llena un QComboBox con todos los tipos de partida únicos. Permite filtrar por proyecto."""
    combo.clear()
    combo.addItem("Todos")

    db = DBManager()
    if id_proyecto is not None:
        query = f"""
            SELECT DISTINCT tipo_partida
            FROM partidas
            WHERE id_proyecto = {id_proyecto}
            ORDER BY tipo_partida
        """
    else:
        query = "SELECT DISTINCT tipo_partida FROM partidas ORDER BY tipo_partida"

    try:
        df = db.obtener_dataframe(query)
        combo.addItems(df["tipo_partida"].fillna("").astype(str))
    except Exception as e:
        print(f"❌ Error al cargar tipos de partida: {e}")

def cargar_id_partidas(combo, id_proyecto=None):
    """Llena un QComboBox con partidas (id + código + nombre), opcionalmente filtradas por proyecto."""
    combo.clear()
    combo.addItem("Todos", "Todos")

    db = DBManager()

    if id_proyecto is not None and id_proyecto != "Todos":
        query = f"""
            SELECT id_partida, codigo_partida, partida_name
            FROM partidas
            WHERE id_proyecto = {int(id_proyecto)}
            ORDER BY id_partida
        """
    else:
        query = """
            SELECT id_partida, codigo_partida, partida_name
            FROM partidas
            ORDER BY id_partida
        """

    try:
        df = db.obtener_dataframe(query)
        for _, row in df.iterrows():
            texto = f"{row['id_partida']} - {row['codigo_partida']} - {row['partida_name']}"
            combo.addItem(texto, row["id_partida"])
    except Exception as e:
        print(f"❌ Error al cargar partidas: {e}")

def cargar_tipos_apus(combo):
    """Llena un QComboBox con los tipos únicos desde la tabla apu_programado."""
    combo.clear()
    combo.addItem("Todos", "Todos")

    db = DBManager()
    try:
        df = db.obtener_dataframe("SELECT DISTINCT tipo FROM apu_programado ORDER BY tipo")
        for tipo in df["tipo"].dropna().astype(str):
            combo.addItem(tipo, tipo)
    except Exception as e:
        print(f"❌ Error al cargar tipos de APU: {e}")
