import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import config


class DBManager:
    def __init__(self):
        self.modo = config.modo_operacion
        self.engine = self._crear_engine()
        self.Session = sessionmaker(bind=self.engine)

    def _crear_engine(self):
        if self.modo == "local":
            print("📡 Modo seleccionado: LOCAL")
            db_url = os.getenv(
                "DB_LOCAL_URL",
                "postgresql://postgres:password@localhost:5432/jergo_local",
            )
            return create_engine(db_url, echo=False, pool_size=1, max_overflow=0)
        else:
            print("📡 Modo seleccionado: NUBE")
            db_url = os.getenv(
                "DB_ONLINE_URL",
                "postgresql://user:pass@host/jergo_db?sslmode=require",
            )
            return create_engine(
                db_url,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                pool_timeout=30,
            )

    def obtener_dataframe(self, query: str, params: dict | None = None) -> pd.DataFrame:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                rows = result.fetchall()
                cols = result.keys()

                def decodificar(valor):
                    if isinstance(valor, bytes):
                        try:
                            return valor.decode("latin1")
                        except Exception:
                            return "??"
                    return valor

                data_limpia = [[decodificar(val) for val in row] for row in rows]
                return pd.DataFrame(data_limpia, columns=cols)
        except Exception as e:
            print(f"❌ Error al obtener DataFrame: {e}")
            return pd.DataFrame()

    def insertar_dataframe(self, df: pd.DataFrame, tabla: str) -> None:
        try:
            df.to_sql(tabla, self.engine, if_exists="append", index=False)
            print(f"✅ Datos insertados en '{tabla}'")
        except SQLAlchemyError as e:
            print(f"❌ Error al insertar en '{tabla}': {e}")

