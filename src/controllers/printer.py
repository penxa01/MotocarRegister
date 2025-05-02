from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPainter, QFont


def dibujar_contenido(self, printer):
    painter = QPainter(printer)

    # Fuente
    painter.setFont(QFont("Arial", 12))

    painter.drawText(500, 1000, "Cliente: Juan Pérez")
    painter.drawText(500, 1500, "Domicio: Calle Falsa 123")
    painter.drawText(2000, 1500, "Documento: 123456789")
    painter.drawText(2000, 2000, "Detalle: Modelo\n Marca motor\n Marca Chasis\n Certificado Nro \n Sin uso y sin faltantes")

    # Dibujar rectángulo por ejemplo
    painter.drawRect(90, 80, 400, 300)

    painter.end()