import os
import pandas as pd
from exportar_exce import exportar_dataframe_a_excel


def test_exportar_crea_archivo(tmp_path):
    df = pd.DataFrame({"a": [1, 2]})
    archivo = tmp_path / "out.xlsx"
    exportar_dataframe_a_excel(df, archivo)
    assert archivo.exists()
