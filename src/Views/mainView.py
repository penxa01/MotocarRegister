import sys
import pandas as pd
import os
import dbf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QDate
import PyQt5.QtGui as Gui
from controllers.MotoRegister import VentanaAgregarRegistro


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Gestión de Registros de Moto")
        self.setWindowIcon(Gui.QIcon("src/assets/motolcosinfondo.ico"))

        self.setMinimumSize(800, 600)
        
        # Variable para rastrear visibilidad de filtros
        self.filtros_visibles = False
        self.dataframeTabla = None

        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout()

        # Agregar logo
        etiqueta_imagen = QLabel(self)
        pixmap = Gui.QPixmap(os.path.join("src/assets", "motocarIcon.png"))
        etiqueta_imagen.setPixmap(pixmap)
        etiqueta_imagen.setAlignment(Qt.AlignCenter)
        etiqueta_imagen.setScaledContents(True)
        etiqueta_imagen.setMaximumHeight(150)
        layout_principal.addWidget(etiqueta_imagen)

        # Layout para botones de acción (PRIMERO)
        layout_botones = QHBoxLayout()
        self.boton_agregar = QPushButton("Agregar registro de moto")
        self.boton_modificar = QPushButton("Modificar")
        self.boton_eliminar = QPushButton("Eliminar")
        self.btn_mostrar_filtros = QPushButton("Filtrar")  # Botón para mostrar/ocultar filtros

        self.boton_agregar.clicked.connect(self.agregar_registro)
        self.boton_modificar.clicked.connect(self.modificar_registro)
        self.boton_eliminar.clicked.connect(self.eliminar_registro)
        self.btn_mostrar_filtros.clicked.connect(self.toggle_filtros)

        layout_botones.addWidget(self.boton_agregar)
        layout_botones.addWidget(self.boton_modificar)
        layout_botones.addWidget(self.boton_eliminar)
        layout_botones.addWidget(self.btn_mostrar_filtros)

        layout_principal.addLayout(layout_botones)

        # Widget contenedor para los filtros (DESPUÉS de los botones de acción)
        self.widget_filtros = QWidget()
        layout_filtros = QHBoxLayout(self.widget_filtros)

        # Configuración de los filtros
        self.input_factura = QLineEdit()
        self.input_remito = QLineEdit()
        self.input_titular = QLineEdit()
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())

        layout_filtros.addWidget(QLabel("Factura:"))
        layout_filtros.addWidget(self.input_factura)
        layout_filtros.addWidget(QLabel("Remito:"))
        layout_filtros.addWidget(self.input_remito)
        layout_filtros.addWidget(QLabel("Titular:"))
        layout_filtros.addWidget(self.input_titular)
        layout_filtros.addWidget(QLabel("Fecha:"))
        layout_filtros.addWidget(self.input_fecha)

        # Agregar el widget de filtros al layout principal DESPUÉS de los botones
        layout_principal.addWidget(self.widget_filtros)
        
        # Ocultar filtros inicialmente
        self.widget_filtros.hide()

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Factura", "Remito", "Titular", "Fecha"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)

        self.tabla.doubleClicked.connect(self.modificar_registro)

        layout_principal.addWidget(self.tabla)

        self.setLayout(layout_principal)

        # Datos de ejemplo
        self.cargar_datos_ejemplo()

    def toggle_filtros(self):
        """Alterna la visibilidad del widget de filtros"""
        self.filtros_visibles = not self.filtros_visibles
        if self.filtros_visibles:
            self.btn_mostrar_filtros.setText("Ocultar Filtros")
            self.widget_filtros.show()
        else:
            self.btn_mostrar_filtros.setText("Filtrar")
            self.widget_filtros.hide()

    def cargar_datos_ejemplo(self):
        # Guardar en DBF
        self.datamoto_path = "D:/tiempo/vtiempo/GESTION/MOTO1718/DATAMOTO.dbf"
        self.datamoto_path = os.path.normpath(self.datamoto_path)
        self.datatitu_path = "D:/tiempo/vtiempo/GESTION/MOTO1718/DATATITU.dbf"
        self.datatitu_path = os.path.normpath(self.datatitu_path)

        if not os.path.exists(self.datamoto_path) or not os.path.exists(self.datatitu_path):
            # Crear DBF si no existe
            self.crear_dbf(self.datamoto_path)
            self.crear_dbf(self.datatitu_path)
        
        self.tabla_registros = dbf.Table(self.datamoto_path)
        self.tabla_registros.open(mode=dbf.READ_ONLY)
        self.tabla_titular = dbf.Table(self.datatitu_path)
        self.tabla_titular.open(mode=dbf.READ_ONLY)

        # Limpiar tabla antes de cargar datos
        self.tabla.setRowCount(0)
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Nroº de chasis", "Modelo", "Titular", "Nroº de Remito","Fecha"])

        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)

        self.dataframeTabla = pd.DataFrame(columns=["Nroº de chasis", "Modelo", "Titular", "Nroº de Remito","Fecha"])
        self.dataframeTabla["Nroº de chasis"] = [registro.NROCHASIS for registro in self.tabla_registros]
        
        for nroChasis in self.dataframeTabla["Nroº de chasis"]:
            # Obtener el modelo correspondiente en la tabla de registros (DBF no tiene atributo query)
            registroModelo = self.tabla_registros['MODELO'].query(f"NROCHASIS == '{nroChasis}'")
            if not registroModelo.empty:
                # Agregar el modelo a la tabla de datos
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Modelo"] = registroModelo.MODELO.values[0]
            # Obtener el registro correspondiente en la tabla de titulares
            registroTitular = self.tabla_titular.query(f"NROCHASIS == '{nroChasis}'")
            if not registroTitular.empty:
                # Agregar el registro a la tabla de datos
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Titular"] = registroTitular.TITULAR.values[0]
            else:
                # Si no se encuentra el registro, asignar un valor vacío
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Titular"] = ""
            #Obtener el remito de entrega correspondiente en la tabla de titulares
            registroRemito = self.tabla_titular.query(f"NROCHASIS == '{nroChasis}'")
            if not registroRemito.empty:
                # Agregar el remito a la tabla de datos
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Nroº de Remito"] = registroRemito.NROREMITO.values[0]
            else:
                # Si no se encuentra el registro, asignar un valor vacío
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Nroº de Remito"] = 'Sin Remito de entrega'
            # Obtener la fecha de entrega correspondiente en la tabla de titulares
            registroFecha = self.tabla_titular.query(f"NROCHASIS == '{nroChasis}'")
            if not registroFecha.empty:
                # Agregar la fecha a la tabla de datos
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Fecha"] = registroFecha.FECHREMITO.values[0]
            else:
                # Si no se encuentra el registro, asignar un valor vacío
                self.dataframeTabla.loc[self.dataframeTabla["Nroº de chasis"] == nroChasis, "Fecha"] = ""

        # Agregar filas desde el DataFrame
        for i, row in self.dataframeTabla.iterrows():
            position = self.tabla.rowCount()
            self.tabla.insertRow(position)
            
            self.tabla.setItem(position, 0, QTableWidgetItem(str(row['Nroº de chasis'])))
            self.tabla.setItem(position, 1, QTableWidgetItem(str(row['Modelo'])))
            self.tabla.setItem(position, 2, QTableWidgetItem(str(row['Titular'])))
            self.tabla.setItem(position, 3, QTableWidgetItem(str(row['Nroº de Remito'])))
            self.tabla.setItem(position, 4, QTableWidgetItem(str(row['Fecha'])))
    
        # Ajustar tamaño de columnas
        self.tabla.resizeColumnsToContents()


    def agregar_registro(self):
        dialogo = VentanaAgregarRegistro(self)
        dialogo.exec_()
        

    def modificar_registro(self):
        fila = self.tabla.currentRow()
        if fila >= 0:
            factura = self.tabla.item(fila, 0).text()
            QMessageBox.information(self, "Modificar", f"Modificar registro con factura {factura}.")
        else:
            QMessageBox.warning(self, "Atención", "Seleccioná un registro para modificar.")

    def eliminar_registro(self):
        fila = self.tabla.currentRow()
        if fila >= 0:
            respuesta = QMessageBox.question(
                self, "Eliminar",
                "¿Estás seguro de que querés eliminar este registro?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.Yes:
                self.tabla.removeRow(fila)
        else:
            QMessageBox.warning(self, "Atención", "Seleccioná un registro para eliminar.")