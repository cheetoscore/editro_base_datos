# -*- coding: utf-8 -*-
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import text
import config
from db import DBManager

def limpiar_filas_subtotales(model):
    for i in reversed(range(model.rowCount())):
        tipo = model.item(i, 3).text().strip().upper()
        if tipo.startswith("SUBTOTAL") or tipo == "TOTAL GENERAL":
            model.removeRow(i)

def recalcular_apu(model):
    db = DBManager()

    try:
        with db.engine.connect() as conn:
            insumos_result = conn.execute(text(f"""
                SELECT LOWER(recurso_name), p_unitario, tipo, unidad
                FROM listado_insumos_programados
                WHERE id_proyecto = {config.id_proyecto_actual}
            """))
            precios_insumos = {
                row[0]: {"precio": float(row[1]), "tipo": row[2], "unidad": row[3]}
                for row in insumos_result
            }

            subtotal_mo = 0.0

            for i in range(model.rowCount()):
                try:
                    id_val = model.item(i, 0).text().strip()
                    recurso = model.item(i, 2).text().strip()
                    tipo = model.item(i, 3).text().strip().upper()
                    unidad = model.item(i, 4).text().strip()
                    cuadrilla = float(model.item(i, 5).text())
                    rendimiento = float(model.item(i, 6).text())
                    cantidad = float(model.item(i, 7).text())
                    precio = float(model.item(i, 8).text())
                except Exception:
                    continue

                recurso_limpio = recurso.lower()

                # Si no es SUB-PARTIDA, obtener datos desde listado_insumos
                if tipo != "SUB-PARTIDA" and recurso_limpio in precios_insumos:
                    datos = precios_insumos[recurso_limpio]
                    tipo = datos["tipo"]
                    unidad = datos["unidad"]
                    precio = datos["precio"]
                    model.setItem(i, 3, QStandardItem(tipo))
                    model.setItem(i, 4, QStandardItem(unidad))
                    model.setItem(i, 8, QStandardItem(f"{precio:.4f}"))

                # Si es SUB-PARTIDA
                if tipo == "SUB-PARTIDA":
                    id_recurso = model.item(i, 1).text()
                    sub_res = conn.execute(text("""
                        SELECT SUM(parcial) FROM sub_apu_programado
                        WHERE codigo_subpartida = :codigo
                    """), {"codigo": id_recurso}).fetchone()
                    precio = float(sub_res[0]) if sub_res and sub_res[0] else 0.0
                    model.setItem(i, 8, QStandardItem(f"{precio:.4f}"))

                # Si es mano de obra o equipo (excepto herramientas manuales)
                if tipo in ["MANO DE OBRA", "EQUIPO"] and recurso.upper() != "HERRAMIENTAS MANUALES":
                    cantidad = cuadrilla / rendimiento if rendimiento else 0.0
                    model.setItem(i, 7, QStandardItem(f"{cantidad:.6f}"))

                # Herramientas manuales (calculado como porcentaje del subtotal MO)
                if recurso.upper() == "HERRAMIENTAS MANUALES" and unidad.upper() == "%MO":
                    porcentaje = cantidad
                    precio = subtotal_mo * porcentaje
                    model.setItem(i, 8, QStandardItem(f"{precio:.4f}"))

                # Calcular parcial
                parcial = cantidad * precio
                model.setItem(i, 9, QStandardItem(f"{parcial:.4f}"))

                if tipo == "MANO DE OBRA":
                    subtotal_mo += parcial

    except Exception as e:
        QMessageBox.critical(None, "Error", f"❌ Error al recalcular APU:\n{e}")

def guardar_apu(model):
    db = DBManager()
    try:
        with db.engine.connect() as conn:
            for i in range(model.rowCount()):
                tipo = model.item(i, 3).text().strip().upper()
                if tipo.startswith("SUBTOTAL") or tipo == "TOTAL GENERAL":
                    continue

                try:
                    id_val = model.item(i, 0).text()
                    campos = {
                        "id_recurso": model.item(i, 1).text(),
                        "recurso_name": model.item(i, 2).text(),
                        "tipo": model.item(i, 3).text(),
                        "unidad": model.item(i, 4).text(),
                        "cuadrilla": float(model.item(i, 5).text()),
                        "rendimiento": float(model.item(i, 6).text()),
                        "cantidad": float(model.item(i, 7).text()),
                        "precio": float(model.item(i, 8).text()),
                        "parcial": float(model.item(i, 9).text()),
                        "id_partida": config.id_partida_actual
                    }

                    if id_val.lower() == "nuevo":
                        columnas = ", ".join(campos.keys())
                        valores = ", ".join([f":{k}" for k in campos])
                        conn.execute(text(f"""
                            INSERT INTO apu_programado ({columnas}) VALUES ({valores})
                        """), campos)
                    else:
                        campos["id"] = int(id_val)
                        conn.execute(text("""
                            UPDATE apu_programado SET
                                id_recurso=:id_recurso,
                                recurso_name=:recurso_name,
                                tipo=:tipo,
                                unidad=:unidad,
                                cuadrilla=:cuadrilla,
                                rendimiento=:rendimiento,
                                cantidad=:cantidad,
                                precio=:precio,
                                parcial=:parcial
                            WHERE id=:id
                        """), campos)

                except Exception as row_error:
                    print(f"⚠️ Error en fila {i}: {row_error}")

        QMessageBox.information(None, "Guardado", "✅ APU guardado correctamente.")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error general al guardar:\n{e}")

