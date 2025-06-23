# Editor Base de Datos

Aplicación de escritorio basada en PyQt5 para la administración de proyectos de construcción. Permite visualizar y editar partidas, APUs e insumos utilizando una base de datos PostgreSQL local u online.

## Requisitos
- Python 3.8+
- PostgreSQL
- Dependencias listadas en `requirements.txt`

## Instalación
```bash
pip install -r requirements.txt
```

## Uso
1. Configure las variables de entorno necesarias (ver más abajo).
2. Ejecute `python main.py` y seleccione el modo de trabajo y el proyecto a editar.
3. Utilice los menús para acceder a las distintas vistas de la aplicación.

## Variables de entorno
- `DB_LOCAL_URL` cadena de conexión para la base de datos local.
- `DB_ONLINE_URL` cadena de conexión para la base de datos en la nube.
- `PG_DUMP_PATH` ruta al ejecutable `pg_dump` utilizado para generar respaldos.
- `PGPASSWORD` contraseña del usuario de la base local (utilizado durante el backup).

## Licencia
Este proyecto se distribuye bajo los términos de la [Licencia MIT](LICENSE).
