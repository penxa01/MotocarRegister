import sys
import pandas as pd
import os
import dbf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QHeaderView ,QMenu, QInputDialog
)
from PyQt5.QtCore import Qt, QDate
import PyQt5.QtGui as Gui
from controllers.MotoRegister import VentanaAgregarRegistro
from controllers.printer import dibujar_contenido
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from controllers.MotoModify import FormularioModificacion
from controllers.Utils import buscar_moto_por_chasis, modificar_moto_en_dbf, buscar_remito_entrega, buscar_moto_titu_por_chasis



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Gestión de Registros de Moto")
        self.setWindowIcon(Gui.QIcon("src/assets/motolcosinfondo.ico"))

        self.setMinimumSize(800, 600)
        
        # Variable para rastrear visibilidad de filtros
        self.filtros_visibles = False
        self.dataframeTabla = None
        self.campos = ["Nroº de chasis",'Modelo', "Remito", "Titular", "Fecha"]
        self.filtros = []

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
        
        # boton de imprimir antes del la foto
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_imprimir.setFixedSize(100, 20)
        layout_principal.addWidget(self.btn_imprimir)
        
        layout_principal.addWidget(etiqueta_imagen)

        # Cargar datos de ejemplo
        self.cargar_datos_ejemplo()
        # Layout para botones de acción (PRIMERO)
        layout_botones = QHBoxLayout()
        self.boton_agregar = QPushButton("Agregar registro de moto")
        self.boton_modificar = QPushButton("Modificar")
        self.boton_eliminar = QPushButton("Eliminar")
        self.btn_mostrar_filtros = QPushButton("Filtrar")  # Botón para mostrar/ocultar filtros
        self.boton_remitosEntrega = QPushButton("Remitos de entrega")

        self.btn_imprimir.clicked.connect(self.imprimir_documento_btn)
        self.boton_agregar.clicked.connect(self.agregar_registro)
        self.boton_modificar.clicked.connect(self.modificar_por_boton)
        self.boton_eliminar.clicked.connect(self.eliminar_registro)
        self.btn_mostrar_filtros.clicked.connect(self.toggle_filtros)
        self.boton_remitosEntrega.clicked.connect(self.remitos_entrega)

        layout_botones.addWidget(self.boton_agregar)
        layout_botones.addWidget(self.boton_modificar)
        layout_botones.addWidget(self.boton_eliminar)
        layout_botones.addWidget(self.boton_remitosEntrega)
        layout_botones.addWidget(self.btn_mostrar_filtros)

        layout_principal.addLayout(layout_botones)
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Nro de chasis",'Modelo', "Remito", "Titular", "Fecha"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.mostrar_menu_contextual)


        

        layout_principal.addWidget(self.tabla)

        self.setLayout(layout_principal)

        # Widget contenedor para los filtros (DESPUÉS de los botones de acción)
        self.widget_filtros = QWidget()
        layout_filtros = QHBoxLayout(self.widget_filtros)

        # Configuración de los filtros
        self.input_chasis = QLineEdit()
        self.input_chasis.textChanged.connect(self.applyFilter)
        self.input_modelo = QLineEdit()
        self.input_modelo.textChanged.connect(self.applyFilter)  # Conectar el evento de texto cambiado
        self.input_remito = QLineEdit()
        self.input_remito.textChanged.connect(self.applyFilter)  # Conectar el evento de texto cambiado
        self.input_titular = QLineEdit()
        self.input_titular.textChanged.connect(self.applyFilter)  # Conectar el evento de texto cambiado
        self.input_fecha = QDateEdit()
        self.input_fecha.setDisplayFormat("dd/MM/yyyy")
        self.input_fecha.dateChanged.connect(self.applyFilter)  # Conectar el evento de texto cambiado
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())

        layout_filtros.addWidget(QLabel("Nro de chasis:"))
        layout_filtros.addWidget(self.input_chasis)
        layout_filtros.addWidget(QLabel("Modelo:"))
        layout_filtros.addWidget(self.input_modelo)
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

        self.update_table(self.dataframeTabla)

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
        # Rutas normalizadas
        self.datamoto_path = os.path.normpath("D:/tiempo/vtiempo/GESTION/MOTO1718/DATAMOTO.dbf")
        self.datatitu_path = os.path.normpath("D:/tiempo/vtiempo/GESTION/MOTO1718/DATATITU.dbf")

        # Crear DBF si no existen
        if not os.path.exists(self.datamoto_path):
            self.crear_dbf(self.datamoto_path)
        if not os.path.exists(self.datatitu_path):
            self.crear_dbf(self.datatitu_path)

        # Abrir tablas DBF
        self.tabla_registros = dbf.Table(self.datamoto_path)
        self.tabla_registros.open(mode=dbf.READ_ONLY)
        self.tabla_titular = dbf.Table(self.datatitu_path)
        self.tabla_titular.open(mode=dbf.READ_ONLY)

        # Extraer datos manualmente campo por campo
        registros = []
        for r in self.tabla_registros:
            try:
                registros.append({
                    "NROCHASIS": r.NROCHASIS.strip() if r.NROCHASIS else "",
                    "MODELO": r.MODELO.strip() if r.MODELO else "",
                })
            except Exception as e:
                print(f"Error leyendo registro: {e}")

        titulares = []
        for t in self.tabla_titular:
            try:
                titulares.append({
                    "NROCHASIS": t.NROCHASIS.strip() if t.NROCHASIS else "",
                    "TITULAR1": t.TITULAR1.strip() if t.TITULAR1 else "",
                    "NROREMITO": t.NROREMITO if t.NROREMITO else "",
                    "FECHAREMIT": t.FECHAREMIT if t.FECHAREMIT else "",
                })
            except Exception as e:
                print(f"Error leyendo titular: {e}")

        datos_registros = pd.DataFrame(registros)
        datos_titular = pd.DataFrame(titulares)

        # Crear DataFrame para tabla
        self.dataframeTabla = datos_registros.copy()
        self.dataframeTabla.rename(columns={"NROCHASIS": "Nroº de chasis", "MODELO": "Modelo"}, inplace=True)
        self.dataframeTabla["Titular"] = ""
        self.dataframeTabla["Nroº de Remito"] = ""
        self.dataframeTabla["Fecha"] = ""

        for i, row in self.dataframeTabla.iterrows():
            nroChasis = row["Nroº de chasis"]
            titular_info = datos_titular[datos_titular["NROCHASIS"] == nroChasis]
            if not titular_info.empty:
                self.dataframeTabla.at[i, "Titular"] = titular_info["TITULAR1"].values[0]
                self.dataframeTabla.at[i, "Nroº de Remito"] = titular_info["NROREMITO"].values[0]
                self.dataframeTabla.at[i, "Fecha"] = titular_info["FECHAREMIT"].values[0]
            else:
                self.dataframeTabla.at[i, "Nroº de Remito"] = "Sin Remito de entrega"


    def agregar_registro(self):
        dialogo = VentanaAgregarRegistro(self)
        dialogo.exec_()
        
    def modificar_por_boton(self):
        chasis, ok = QInputDialog.getText(self, "Modificar", "Ingrese número de chasis:")
        if ok and chasis:
            datos = buscar_moto_por_chasis(chasis)
            if datos:
                self.abrir_formulario_modificacion(datos)
            else:
                QMessageBox.warning(self, "No encontrado", "No se encontró ese número de chasis.")
    
    def mostrar_menu_contextual(self, posicion):
        menu = QMenu()
        accion_modificar = menu.addAction("Modificar registro")
        accion_eliminar = menu.addAction("Eliminar registro")
        accion_imprimir = menu.addAction("Imprimir Remito")
        accion = menu.exec_(self.tabla.viewport().mapToGlobal(posicion))
        if accion == accion_imprimir:
            self.imprimir_documento_tabla(self.tabla.currentRow())
        if accion == accion_eliminar:
            self.eliminar_registro_tabla(self.tabla.currentRow())
        if accion == accion_modificar:
            self.modificar_desde_tabla(self.tabla.currentRow())

    def modificar_desde_tabla(self,fila):
        chasis = self.tabla.item(fila, 0).text()
        datos = buscar_moto_por_chasis(chasis)
        if datos:
            self.abrir_formulario_modificacion(datos)
        else:
            QMessageBox.warning(self, "No encontrado", "No se encontró ese número de chasis.")
    
    def abrir_formulario_modificacion(self, datos):
        def callback_guardar(nuevos_datos):
            modificar_moto_en_dbf(nuevos_datos)
            QMessageBox.information(self, "Éxito", "Moto modificada con éxito.")
            self.cargar_datos_ejemplo()
            self.update_table(self.dataframeTabla)  # O refrescar tabla si lo tenés

        form = FormularioModificacion(datos, callback_guardar)
        form.exec_()


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
    
    def update_table(self,datos):
        # Preparar tabla visual
        self.tabla.clear()
        self.tabla.setRowCount(0)
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Nroº de chasis", "Modelo", "Titular", "Nroº de Remito", "Fecha"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        # Actualiza la tabla con los datos filtrados
        self.tabla.setRowCount(0)
        for i, row in datos.iterrows():
            position = self.tabla.rowCount()
            self.tabla.insertRow(position)
            self.tabla.setItem(position, 0, QTableWidgetItem(str(row["Nroº de chasis"])))
            self.tabla.setItem(position, 1, QTableWidgetItem(str(row["Modelo"])))
            self.tabla.setItem(position, 2, QTableWidgetItem(str(row["Titular"])))
            self.tabla.setItem(position, 3, QTableWidgetItem(str(row["Nroº de Remito"])))
            self.tabla.setItem(position, 4, QTableWidgetItem(str(row["Fecha"])))
        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def applyFilter(self):
        chasis = self.input_chasis.text().strip().lower()
        modelo = self.input_modelo.text().strip().lower()
        titular = self.input_titular.text().strip().lower()
        remito = self.input_remito.text().strip().lower()
        fecha_qdate = self.input_fecha.date()
        fecha_str = fecha_qdate.toString("yyyy-MM-dd")

        # Normalizar y formatear columna Fecha como string
        df = self.dataframeTabla.copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce').dt.strftime("%Y-%m-%d")

        # Aplicar filtros uno por uno
        df_filtrado = df[
            df["Nroº de chasis"].str.lower().str.contains(chasis, na=False) &
            df["Modelo"].str.lower().str.contains(modelo, na=False) &
            df["Titular"].str.lower().str.contains(titular, na=False) &
            df["Nroº de Remito"].astype(str).str.lower().str.contains(remito, na=False)
        ]

        # Si se seleccionó una fecha distinta al día de hoy, aplicar filtro
        if fecha_str != QDate.currentDate().toString("yyyy-MM-dd"):
            df_filtrado = df_filtrado[df_filtrado["Fecha"] == fecha_str]

        self.update_table(df_filtrado)
    
    def imprimir_documento_btn(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Buscar Remito de Entrega")
        dialogo.setFixedWidth(300)

        layout = QVBoxLayout()

        input_chasis = QLineEdit()
        input_remito = QLineEdit()
        input_punto = QLineEdit()

        layout.addWidget(QLabel("Nro de Chasis:"))
        layout.addWidget(input_chasis)

        layout.addWidget(QLabel("Nro de Remito:"))
        layout.addWidget(input_remito)

        layout.addWidget(QLabel("Punto de Venta:"))
        layout.addWidget(input_punto)

        boton_buscar = QPushButton("Imprimir")

        def al_hacer_click():
            chasis = input_chasis.text().strip()
            remito = int(input_remito.text())
            punto = int(input_punto.text())
            self.imprimir_por_boton(chasis, remito, punto)   

        boton_buscar.clicked.connect(al_hacer_click)
        layout.addWidget(boton_buscar)

        dialogo.setLayout(layout)
        dialogo.exec_()

    def imprimir_documento_tabla(self, fila):
        chasis = self.tabla.item(fila, 0).text()
        datos_titular = buscar_moto_titu_por_chasis(chasis)
        datos_moto = buscar_moto_por_chasis(chasis)
        if datos_titular and datos_moto:
            self.imprimir_documento(datos_moto,datos_titular)
        else:
            QMessageBox.warning(self, "No encontrado", "No se encontró ese número de chasis.")
    
    def imprimir_por_boton(self,nrochasis, remitoEntrega, ptoventa):
        titular = buscar_moto_titu_por_chasis(nrochasis)
        moto = buscar_moto_por_chasis(nrochasis)
        print(titular['NROCHASIS'].strip())
        print(nrochasis)
        print(titular['NROREMITO'])
        print(remitoEntrega)
        print(titular['PTOREMITO'])
        print(ptoventa)
        if titular['TITULAR1'] is None or titular['TITULAR1'] == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("El chasis ingresado no tiene titular asociado.")
            msg.exec_()
        elif titular['NROCHASIS'].strip() == nrochasis and titular['NROREMITO'] == remitoEntrega and int(titular['PTOREMITO']) == ptoventa:
            self.imprimir_documento(moto,titular)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("Los datos son erroneos")
            msg.exec_()

    def imprimir_documento(self,moto,titular):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)
        printer.setFullPage(False)

        painter = Gui.QPainter()
        if painter.begin(printer):
            dibujar_contenido(painter, printer,moto,titular)
            painter.end()

    def remitos_entrega(self):

        dialogo = QDialog(self)
        dialogo.setWindowTitle("Buscar Remito de Entrega")
        dialogo.setFixedWidth(300)

        layout = QVBoxLayout()

        input_chasis = QLineEdit()
        input_remito = QLineEdit()
        input_punto = QLineEdit()

        layout.addWidget(QLabel("Nro de Chasis:"))
        layout.addWidget(input_chasis)

        layout.addWidget(QLabel("Nro de Remito:"))
        layout.addWidget(input_remito)

        layout.addWidget(QLabel("Punto de Venta:"))
        layout.addWidget(input_punto)

        boton_buscar = QPushButton("Buscar")

        def al_hacer_click():
            chasis = input_chasis.text().strip()
            remito = int(input_remito.text())
            punto = int(input_punto.text())
            buscar_remito_entrega(chasis, punto, remito)

        boton_buscar.clicked.connect(al_hacer_click)
        layout.addWidget(boton_buscar)

        dialogo.setLayout(layout)
        dialogo.exec_()