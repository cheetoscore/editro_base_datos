import os
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# 📌 Configuración de conexión mediante variables de entorno
DB_LOCAL_URL = os.getenv("DB_LOCAL_URL", "postgresql://postgres:password@localhost/jergo_local")
DB_ONLINE_URL = os.getenv("DB_ONLINE_URL", "postgresql://user:pass@host/jergo_db?sslmode=require")

engine_local = create_engine(DB_LOCAL_URL, pool_pre_ping=True)
engine_online = create_engine(DB_ONLINE_URL, pool_pre_ping=True)

# 🔁 Orden correcto de tablas según relaciones foráneas
ORDEN_DEPENDENCIAS = [
    "usuarios",
    "proyectos",
    "partidas",
    "ingresos",
    "ingresos_reales",
    "apu_programado",
    "sub_apu_programado",
    "cronograma_meta",
    "crono_matris_p",
    "msproject",
    "valorizaciones",
    "pronostico_ingresos",
    "programacion_ingresos",
    "apu_contrato",
    "crono_matriz_c",
    "sub_apu_contrato",
    "apu_historico",
    "recursos_programados",
    "requerimientos",
    "db_insumos_programados",
    "db_insumos_gastados",
    "listado_insumos_programados",
]


def obtener_tablas(direccion: str = "online"):
    """Retorna una lista de todas las tablas en la base seleccionada."""
    engine = engine_online if direccion == "online" else engine_local
    inspector = inspect(engine)
    return inspector.get_table_names(schema="public")


def ordenar_tablas(tablas: list) -> list:
    """Ordena las tablas según la jerarquía de dependencias."""
    ordenadas = [t for t in ORDEN_DEPENDENCIAS if t in tablas]
    restantes = [t for t in tablas if t not in ordenadas]
    return ordenadas + restantes


def sincronizar(tablas: list, direccion: str = "local_a_online"):
    """Sincroniza datos entre base local y NEON sin borrar las tablas."""
    errores: list[tuple[str, str]] = []
    tablas_ordenadas = ordenar_tablas(tablas)

    for tabla in tablas_ordenadas:
        try:
            if direccion == "local_a_online":
                origen = engine_local
                destino = engine_online
                print(f"⬆️ Subiendo '{tabla}' de LOCAL a NEON...")
            elif direccion == "online_a_local":
                origen = engine_online
                destino = engine_local
                print(f"⬇️ Descargando '{tabla}' de NEON a LOCAL...")
            else:
                raise ValueError("Dirección inválida: usa 'local_a_online' o 'online_a_local'")

            df = pd.read_sql(f"SELECT * FROM {tabla}", origen)

            with destino.begin() as conn:
                conn.execute(text(f"DELETE FROM {tabla}"))

            df.to_sql(tabla, destino, if_exists="append", index=False)
            print(f"✅ '{tabla}' sincronizada correctamente.")
        except SQLAlchemyError as e:
            errores.append((tabla, str(e)))
            print(f"❌ Error al sincronizar '{tabla}': {e}")

    if errores:
        print("\n🚨 Errores durante la sincronización:")
        for tabla, msg in errores:
            print(f" - {tabla}: {msg}")

