"""Funciones para exportar datos a Excel."""

import pandas as pd


def exportar_dataframe_a_excel(df: pd.DataFrame, ruta: str) -> None:
    """Exporta un DataFrame a un archivo .xlsx."""
    df.to_excel(ruta, index=False, engine="openpyxl")
