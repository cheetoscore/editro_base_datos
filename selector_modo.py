from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class SelectorModoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar Modo de Trabajo")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        label = QLabel("¿Desea trabajar en modo Local o Online?")
        layout.addWidget(label)

        btn_local = QPushButton("🌐 Modo Local")
        btn_online = QPushButton("☁️ Modo Online")

        btn_local.clicked.connect(self.set_local)
        btn_online.clicked.connect(self.set_online)

        layout.addWidget(btn_local)
        layout.addWidget(btn_online)

        self.setLayout(layout)

    def set_local(self):
        import config
        config.modo_trabajo = "local"
        print("📡 Modo seleccionado: LOCAL")  # debug
        self.accept()

    def set_online(self):
        import config
        config.modo_trabajo = "online"
        print("📡 Modo seleccionado: ONLINE")  # debug
        self.accept()

