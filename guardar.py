from db import DBManager
from sqlalchemy.exc import SQLAlchemyError
import config

# Instanciar el gestor de base de datos (puedes cambiar a "local" si deseas trabajar en local)
db = DBManager()

def guardar_dataframe(df, tabla):

    try:
        df.to_sql(tabla, db.engine, if_exists='replace', index=False)
        print(f"✅ Datos guardados correctamente en la tabla '{tabla}'")
    except SQLAlchemyError as e:
        print(f"❌ Error al guardar en la tabla '{tabla}': {e}")

def agregar_datos(df, tabla):

    try:
        df.to_sql(tabla, db.engine, if_exists='append', index=False)
        print(f"✅ Registros agregados a '{tabla}'")
    except SQLAlchemyError as e:
        print(f"❌ Error al insertar en la tabla '{tabla}': {e}")


