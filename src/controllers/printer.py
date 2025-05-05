from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPainter, QFont


def dibujar_contenido(painter, printer):
    painter.setFont(QFont("Arial", 12))

    painter.drawText(3200, 1005, ": 15/15/2025")
    painter.drawText(835, 1528, "Juan Pérez")
    painter.drawText(835, 1710, "Calle Falsa 123")
    painter.drawText(2667, 1807, ": 123456789")
    painter.drawText(2350, 2800, "Detalle: Modelo\n")
    painter.drawText(2350, 2900, "Marca motor: Hotwheels\n")
    painter.drawText(2350, 3000, "Marca chasis: Ejemplo\n")
    painter.drawText(2350, 3100, "Certificado Nro:15965dfdsfd/ 152515 \n")
    painter.drawText(2350, 3200, "Sin uso y sin faltantes\n")

    painter.drawRect(90, 80, 400, 300)