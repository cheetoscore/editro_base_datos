# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QDialog
from vista_editor_proyectos import crear_editor_proyectos
from vista_editor_partidas import crear_editor_partidas
from vista_editor_apus import crear_editor_apus
from vista_editor_insumos import crear_editor_insumos
from selector_proyecto import SelectorProyectoDialog  # ✅ nuevo
import config  
from vista_sincronizador import crear_sincronizador_ui
from selector_modo import SelectorModoDialog

config.modo_operacion = "local"  # o "nube"
print(f"📡 Modo global establecido: {config.modo_operacion}")

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.actualizar_titulo()
        self.setGeometry(100, 100, 1000, 600)
        self.init_menu()

    def actualizar_titulo(self):
        modo = config.modo_trabajo
        if modo == "local":
            modo_texto = "🌐 Modo Local"
        elif modo == "online":
            modo_texto = "☁️ Modo Online"
        else:
            modo_texto = "❓ Modo Desconocido"

        self.setWindowTitle(f"Editor Base de Datos - Jergo | {modo_texto} | Proyecto: {config.nombre_proyecto_actual}")

    def init_menu(self):
        menubar = self.menuBar()

        # 📊 Nuevo Menú Principal
        menu_presupuesto = menubar.addMenu("📊 Presupuesto Meta")

        action_proyectos = QAction("🧱 Proyectos", self)
        action_proyectos.triggered.connect(self.mostrar_proyectos)
        menu_presupuesto.addAction(action_proyectos)

        action_partidas = QAction("📦 Partidas", self)
        action_partidas.triggered.connect(self.mostrar_partidas)
        menu_presupuesto.addAction(action_partidas)

        action_apus = QAction("📐 APU Programado", self)
        action_apus.triggered.connect(self.mostrar_apus)
        menu_presupuesto.addAction(action_apus)

        action_insumos = QAction("🧾 Insumos (Recursos)", self)
        action_insumos.triggered.connect(self.mostrar_insumos)
        menu_presupuesto.addAction(action_insumos)

        # Menú de opciones generales
        menu_opciones = menubar.addMenu("⚙️ Opciones")
        action_cambiar = QAction("🔁 Cambiar Proyecto", self)
        action_cambiar.triggered.connect(self.cambiar_proyecto)
        menu_opciones.addAction(action_cambiar)
        
        menu_db = menubar.addMenu("🗄️ DataBase")
        action_sync = QAction("🔁 Sincronizar BD", self)
        action_sync.triggered.connect(lambda: self.setCentralWidget(crear_sincronizador_ui()))
        menu_db.addAction(action_sync)

    def mostrar_proyectos(self):
        widget = crear_editor_proyectos()
        self.setCentralWidget(widget)

    def mostrar_partidas(self):
        if config.id_proyecto_actual is None:
            self.setWindowTitle("⚠️ No se ha seleccionado un proyecto")
            return
        widget = crear_editor_partidas()
        self.setCentralWidget(widget)

    def mostrar_apus(self):
        if config.id_proyecto_actual is None:
            self.setWindowTitle("⚠️ No se ha seleccionado un proyecto")
            return
        widget = crear_editor_apus()
        self.setCentralWidget(widget)

    def mostrar_insumos(self):
        if config.id_proyecto_actual is None:
            self.setWindowTitle("⚠️ No se ha seleccionado un proyecto")
            return
        widget = crear_editor_insumos()
        self.setCentralWidget(widget)

    def cambiar_proyecto(self):
        dialogo = SelectorProyectoDialog()
        if dialogo.exec_() == QDialog.Accepted:
            self.setWindowTitle(f"Editor Base de Datos - Jergo | Proyecto: {config.nombre_proyecto_actual}")
            self.setCentralWidget(None)  # Limpia contenido al cambiar proyecto

def main():
    app = QApplication(sys.argv)

    # Paso 1: Selección de modo
    selector_modo = SelectorModoDialog()
    if selector_modo.exec_() != QDialog.Accepted:
        sys.exit()

    import config
    print("Modo seleccionado:", config.modo_trabajo)  # Debug

    # Paso 2: Selección de proyecto
    selector_proyecto = SelectorProyectoDialog()
    if selector_proyecto.exec_() != QDialog.Accepted:
        sys.exit()

    # Paso 3: Lanzar ventana principal
    ventana = MainMenu()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
