# Agregá estas importaciones si no están:
from PyQt5.QtWidgets import QDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QDate, Qt

class VentanaAgregarRegistro(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar nuevo registro")
        self.setMinimumSize(300, 200)

        self.layout = QVBoxLayout()

        formulario = QFormLayout()
        self.input_factura = QLineEdit()
        self.input_remito = QLineEdit()
        self.input_titular = QLineEdit()
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())

        formulario.addRow("Factura:", self.input_factura)
        formulario.addRow("Remito:", self.input_remito)
        formulario.addRow("Titular:", self.input_titular)
        formulario.addRow("Fecha:", self.input_fecha)

        self.layout.addLayout(formulario)

        botones = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        self.layout.addLayout(botones)

        self.setLayout(self.layout)

        # Conexión de botones
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self.guardar_registro)

    def guardar_registro(self):
        datos = (
            self.input_factura.text(),
            self.input_remito.text(),
            self.input_titular.text(),
            self.input_fecha.date().toString("yyyy-MM-dd")
        )

        if all(datos[:3]):  # Verifica que no estén vacíos los campos principales
            self.datos_nuevos = datos
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Completá todos los campos.")

