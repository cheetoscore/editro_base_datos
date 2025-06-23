from sincronizador import ordenar_tablas


def test_ordenar_tablas():
    tablas = ["b", "usuarios", "msproject", "apu_historico"]
    ordenadas = ordenar_tablas(tablas)
    assert ordenadas[0] == "usuarios"
    assert "msproject" in ordenadas
