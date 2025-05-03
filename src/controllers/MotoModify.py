from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QDateEdit
from PyQt5.QtCore import QDate

class FormularioModificacion(QDialog):
    def __init__(self, datos_moto, on_guardar_callback):
        super().__init__()
        self.setWindowTitle("Modificar Registro")
        self.datos_moto = datos_moto
        self.on_guardar_callback = on_guardar_callback
        self.inputs = {}

        # Etiquetas legibles para el usuario
        etiquetas = {
            "REMITOING": "Remito de Ingreso",
            "FECHREMITO": "Fecha Remito",
            "MARCAMOTO": "Marca Moto",
            "MODELO": "Modelo",
            "MARCAMOTOR": "Marca Motor",
            "NROMOTOR": "Nroº de Motor",
            "MARCACHASI": "Marca Chasis",
            "NROCHASIS": "Nroº de Chasis",
            "TIPOMOTO": "Tipo de Moto",
            "NROCERTIFI": "Certificado",
            "COLOR": "Color",
            "FECHALTA": "Fecha de Alta",
            "ESTADO": "Estado",
            "NRODEMOTO": "Nroº de moto",
            "DEPOSITO": "Depósito"
        }

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        for campo, valor in datos_moto.items():
            etiqueta = etiquetas.get(campo, campo)

            if "FECH" in campo and valor and valor != "None":
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("yyyy-MM-dd")
                try:
                    partes = valor.split("-")
                    if len(partes) == 3:
                        date_edit.setDate(QDate(int(partes[0]), int(partes[1]), int(partes[2])))
                except:
                    date_edit.setDate(QDate.currentDate())
                self.inputs[campo] = date_edit
                form_layout.addRow(etiqueta, date_edit)
            else:
                line_edit = QLineEdit("" if valor == "None" else str(valor))
                self.inputs[campo] = line_edit
                form_layout.addRow(etiqueta, line_edit)

        layout.addLayout(form_layout)

        btn_guardar = QPushButton("Guardar cambios")
        btn_guardar.clicked.connect(self.guardar_cambios)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)

    def guardar_cambios(self):
        nuevos_datos = {}
        for campo, widget in self.inputs.items():
            if isinstance(widget, QDateEdit):
                nuevos_datos[campo] = widget.date().toString("yyyy-MM-dd")
            else:
                nuevos_datos[campo] = widget.text()
        self.on_guardar_callback(nuevos_datos)
        self.accept()
