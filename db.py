from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import config
import pandas as pd

class DBManager:
    def __init__(self):
        self.modo = config.modo_operacion
        self.engine = self._crear_engine()
        self.Session = sessionmaker(bind=self.engine)

    def _crear_engine(self):
        if self.modo == "local":
            print("📡 Modo seleccionado: LOCAL")
            # Reemplaza con tus datos reales
            db_url = "postgresql://postgres:1113@localhost:5432/jergo_local?client_encoding=latin1"
            return create_engine(db_url, echo=False, pool_size=1, max_overflow=0)
        else:
            print("📡 Modo seleccionado: NUBE")
            db_url = (
                "postgresql://jergo_db_owner:npg_p0Shbuz1Nijq@ep-bitter-glade-a5fgh7ka-pooler.us-east-2.aws.neon.tech/jergo_db?sslmode=require"
            )
            return create_engine(db_url, pool_size=10, max_overflow=20, pool_recycle=1800, pool_timeout=30)

    def obtener_dataframe(self, query):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))  # ✅ CORREGIDO: usar text() para ejecutar la consulta
                rows = result.fetchall()
                cols = result.keys()

                # Decodificación manual si hay valores tipo bytes
                def decodificar(valor):
                    if isinstance(valor, bytes):
                        try:
                            return valor.decode("latin1")
                        except:
                            return "??"
                    return valor

                data_limpia = [[decodificar(val) for val in row] for row in rows]
                return pd.DataFrame(data_limpia, columns=cols)

        except Exception as e:
            print(f"❌ Error al obtener DataFrame: {e}")
            return pd.DataFrame()

    def insertar_dataframe(self, df, tabla):
        try:
            df.to_sql(tabla, self.engine, if_exists="append", index=False)
            print(f"✅ Datos insertados en '{tabla}'")
        except SQLAlchemyError as e:
            print(f"❌ Error al insertar en '{tabla}': {e}")
