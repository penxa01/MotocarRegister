from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPainter, QFont


def dibujar_contenido(painter, printer,moto, titular):
    painter.setFont(QFont("Arial", 12))

    painter.drawText(3200, 1005, f":{titular['FECHAREMIT']}")
    painter.drawText(835, 1528, f":{titular['TITULAR1']}")
    painter.drawText(835, 1710, f":{titular['DOMICILIO1']}")
    painter.drawText(2667, 1807, f"DNI: {titular['NRODOC1']}")
    painter.drawText(2350, 2800, "Tipo Motocicleta 0 Km\n")
    painter.drawText(2350, 2900, f"Marca moto: {moto['MARCAMOTO']}\n")
    painter.drawText(2350, 3000, f"Modelo: {moto['MODELO']}\n")
    painter.drawText(2350, 3100, f"Marca de motor:{moto['MARCAMOTOR']} Nro:{moto['NROMOTOR']}\n")
    painter.drawText(2350, 3200, f"Marca de chasis:{moto['MARCACHASI']} Nro:{moto['NROCHASIS']}\n")
    painter.drawText(2350, 3300, "Sin uso y sin faltantes\n")

    painter.drawRect(90, 80, 400, 300)