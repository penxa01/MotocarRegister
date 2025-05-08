from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate
import dbf
import os

class VentanaAgregarRegistro(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar nueva moto")
        self.setMinimumSize(400, 500)

        self.layout = QVBoxLayout()

        self.formulario = QFormLayout()

        self.inputs = {}

        # Guardar en DBF
        self.dbf_path = "D:/tiempo/vtiempo/GESTION/MOTO1718/DATAMOTO.dbf"
        self.dbf_path = os.path.normpath(self.dbf_path)

        if not os.path.exists(self.dbf_path):
            self.crear_dbf(self.dbf_path)
        
        self.tabla = dbf.Table(self.dbf_path)
        self.tabla.open(mode=dbf.READ_WRITE)

        # Relacionar nombre interno con nombre de etiqueta
        self.campos = [
            ("REMITOING", "Remito de Ingreso", QLineEdit()),
            ("FECHREMITO", "Fecha Remito", QDateEdit()),
            ("MARCAMOTO", "Marca Moto", QLineEdit()),
            ("MODELO", "Modelo", QLineEdit()),
            ("MARCAMOTOR", "Marca Motor", QLineEdit()),
            ("NROMOTOR", "Nroº de Motor", QLineEdit()),
            ("MARCACHASI", "Marca Chasis", QLineEdit()),
            ("NROCHASIS", "Nroº de Chasis", QLineEdit()),
            ("TIPOMOTO", "Tipo de Moto", QLineEdit()),
            ("NROCERTIFI", "Certificado", QLineEdit()),
            ("COLOR", "Color", QLineEdit()),
            ("FECHALTA", "Fecha de Alta", QDateEdit()),
            ("NRODEMOTO", "Nroº de moto", QLineEdit()),
            ("DEPOSITO", "Depósito", QLineEdit()),
        ]

        for clave, etiqueta, widget in self.campos:
            if isinstance(widget, QDateEdit):
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
            self.inputs[clave] = widget
            self.formulario.addRow(etiqueta + ":", widget)

        self.layout.addLayout(self.formulario)

        # Botones
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
        # Crear el diccionario con los valores
        datos = {}
        for campo, widget in self.inputs.items():
            if isinstance(widget, QDateEdit):
                datos[campo] = widget.date().toString("yyyyMMdd")  # Formato compatible DBF (AAAAMMDD)
            else:
                datos[campo] = widget.text()

        # Validación básica
        campos_obligatorios = ["REMITOING", "MARCAMOTO", "MODELO", "NROMOTOR", "NROCHASIS"]
        for campo in campos_obligatorios:
            if not datos.get(campo):
                QMessageBox.warning(self, "Error", f"El campo {campo} no puede estar vacío.")
                return

        try:
            # Verificar si nro de chasis ya existe
            self.verificar_chasis(datos["NROCHASIS"])

            self.tabla.append((
                int(datos["REMITOING"]),
                self.dbf_fecha(datos["FECHREMITO"]),
                datos["MARCAMOTO"],
                datos["MODELO"],
                datos["MARCAMOTOR"],
                datos["NROMOTOR"],
                datos["MARCACHASI"],
                datos["NROCHASIS"],
                datos["TIPOMOTO"],
                datos["NROCERTIFI"],
                datos["COLOR"],
                self.dbf_fecha(datos["FECHALTA"]),
                0,
                int(datos["NRODEMOTO"]) if datos["NRODEMOTO"] else 0,
                int(datos["DEPOSITO"]) if datos["DEPOSITO"] else 0,
            ))
            self.tabla.close()
            self.insert_datatitu(datos["NROCHASIS"],datos["NROCERTIFI"])

            QMessageBox.information(self, "Éxito", "Moto agregada correctamente.")
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Tipo de dato incorrecto:\n{str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Error al guardar", f"Ocurrió un error al guardar los datos:\n{str(e)}")
            

    def dbf_fecha(self, texto_fecha):
        from datetime import datetime
        return datetime.strptime(texto_fecha, "%Y%m%d")
    
    def insert_datatitu(self, nrochasis, nrocertifi):
        dbf_path = "D:/tiempo/vtiempo/GESTION/MOTO1718/DATATITU.dbf"
        dbf_path = os.path.normpath(dbf_path)

        if not os.path.exists(dbf_path):
            self.crear_dbf(dbf_path)

        try:
            tabla = dbf.Table(dbf_path)
            tabla.open(mode=dbf.READ_WRITE)
            nueva_fila = (
            nrochasis,     # NROCHASIS (C:20)
            '',            # LETRAFACTU (C:1)
            '',            # PTOFACTURA (C:4)
            0,             # NROFACTURA (N:8.0)
            None,          # FECHAFACTU (D:8)
            '',            # PTOREMITO (C:4)
            0,             # NROREMITO (N:8.0)
            None,          # FECHAREMIT (D:8)
            '',            # TITULAR1 (C:50)
            '',            # DOMICILIO1 (C:40)
            '',            # LOCALIDAD1 (C:25)
            '',            # CODPOSTAL1 (C:8)
            '',            # PROVINCIA1 (C:20)
            0,             # TIPDOC1 (N:1.0)
            0,             # NRODOC1 (N:11.0)
            '',            # TELEFONO1 (C:20)
            '',            # TITULAR2 (C:50)
            '',            # DOMICILIO2 (C:40)
            '',            # LOCALIDAD2 (C:25)
            '',            # CODPOSTAL2 (C:8)
            '',            # PROVINCIA2 (C:20)
            0,             # TIPDOC2 (N:1.0)
            0,             # NRODOC2 (N:11.0)
            '',            # TELEFONO2 (C:20)
            nrocertifi,    # NROCERTIFI (C:25)
            0.0,           # IMPOVTA (N:12.2)
            None,          # FECHAREGIS (D:8)
            '',            # DOMINIO (C:6)
            '',            # NROREGISTR (C:2)
            0.0,           # NETOVTA (N:10.2)
            0.0,           # TIVAVTA (N:10.2)
            '',            # CUITVTA (C:15)
        )
            tabla.append(nueva_fila)
            tabla.close()
        except Exception as e:
            QMessageBox.warning(self, "Error al guardar", f"Ocurrió un error al guardar los datos:\n{str(e)}")
            if tabla and tabla.status == dbf.READ_WRITE:
                tabla.close()

    def verificar_chasis(self, nro_chasis):
        # Verificar si el chasis ya existe en la tabla
        for registro in self.tabla:
            if registro.NROCHASIS.strip() == nro_chasis.strip():
                raise ValueError(f"El chasis {nro_chasis} ya existe en la base de datos.")
