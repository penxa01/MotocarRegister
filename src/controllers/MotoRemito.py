from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import dbf

def mostrar_datos_titulares(nrochasis, datos_cliente):
    nombres_formales = {
        "TITULAR1": "Nombre",
        "DOMICILIO1": "Domicilio",
        "LOCALIDAD1": "Localidad",
        "CODPOSTAL1": "Código Postal",
        "PROVINCIA1": "Provincia",
        "TIPODOC1": "Tipo de Documento",
        "NRODOC1": "Nº Documento",
        "TELEFONO1": "Teléfono"
    }

    #Convierte campos_titular2 a diccionario
    campos_titular2 = {
        'TITULAR2': 'Nombre',
        'DOMICILIO2': 'Domicilio',
        'LOCALIDAD2': 'Localidad',
        'CODPOSTAL2': 'Código Postal',
        'PROVINCIA2': 'Provincia',
        'TIPODOC2': 'Tipo de Documento',
        'NRODOC2': 'Nº Documento',
        'TELEFONO2': 'Teléfono'
    }

    ventana = QDialog()
    ventana.setWindowTitle("Datos del Titular")

    # Layouts principales
    layout_principal = QVBoxLayout()
    layout_contenido = QHBoxLayout()

    # Columna Titular 1
    col1 = QVBoxLayout()
    col1.addWidget(QLabel("Datos del Titular 1"))
    for campo, nombre_formal in nombres_formales.items():
        valor = datos_cliente.get(campo, "")
        col1.addWidget(QLabel(f"{nombre_formal}: {valor}"))

    # Columna Titular 2
    col2 = QVBoxLayout()
    col2.addWidget(QLabel("Datos del Titular 2"))
    entradas_titular2 = {}
    for campo, nombre_formal in nombres_formales.items():
        campo2 = campo.replace("1", "2")
        input_field = QLineEdit()
        input_field.setText(datos_cliente.get(campo2, ""))  # Mostrar si hay datos
        col2.addWidget(QLabel(nombre_formal + ":"))
        col2.addWidget(input_field)
        entradas_titular2[campo2] = input_field

    layout_contenido.addLayout(col1)
    layout_contenido.addLayout(col2)

    def guardar_datos():
        try:
            tabla = dbf.Table("D:/tiempo/vtiempo/GESTION/MOTO1718/DATATITU.dbf")
            tabla.open(mode=dbf.READ_WRITE)
            encontrado = False
            for record in tabla:
                if record.NROCHASIS.strip() == nrochasis.strip():
                    with record:
                        for campo, widget in entradas_titular2.items():
                            valor = widget.text().strip()
                            if campo in tabla.field_names:
                                if campo in ["TIPODOC2", "NRODOC2"]:
                                    try:
                                        valor = int(valor)
                                    except ValueError:
                                        valor = 0
                                else:
                                    valor = valor if valor != "" else ""
                                setattr(record, campo, valor)
                    encontrado = True
                    break
            tabla.close()
            if encontrado:
                QMessageBox.information(ventana, "Éxito", "Datos del segundo titular guardados.")
                ventana.accept()
            else:
                QMessageBox.warning(ventana, "Error", "No se encontró el nro de chasis.")
        except Exception as e:
            QMessageBox.critical(ventana, "Error", f"Ocurrió un error: {str(e)}")
    # Botón Aceptar
    boton_guardar = QPushButton("Aceptar")
    boton_guardar.clicked.connect(guardar_datos)
    layout_principal.addLayout(layout_contenido)
    layout_principal.addWidget(boton_guardar)
    ventana.setLayout(layout_principal)

    ventana.exec_()
