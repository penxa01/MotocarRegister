from datetime import datetime
import os
import dbf
from controllers.MotoRemito import mostrar_datos_titulares
from dbfread import DBF
#import para QwarningBox aqui
from PyQt5.QtWidgets import QMessageBox



def modificar_moto_en_dbf(nuevos_datos):
    import dbf

    db = dbf.Table("D:/tiempo/vtiempo/GESTION/MOTO1718/DATAMOTO.dbf")
    db.open(mode=dbf.READ_WRITE)

    for record in db:
        if record.NROCHASIS.strip() == nuevos_datos["NROCHASIS"].strip():
            print(nuevos_datos)
            with record:
                for campo in nuevos_datos:
                    if campo in db.field_names:
                        valor = nuevos_datos[campo]
                        if valor == "None" or valor == "":
                            valor = None
                        elif campo.startswith("FECH"):  # detectar campos de fecha
                            try:
                                valor = datetime.strptime(valor, "%Y-%m-%d").date()
                            except Exception:
                                valor = None
                        setattr(record, campo, valor)
            break

    db.close()

def buscar_moto_por_chasis(numero_chasis):
    for registro in DBF("D:/tiempo/vtiempo/GESTION/MOTO1718/DATAMOTO.dbf"):
        if registro["NROCHASIS"].strip() == numero_chasis.strip():
            return dict(registro)
    return None

def buscar_moto_titu_por_chasis(numero_chasis):
    for registro in DBF("D:/tiempo/vtiempo/GESTION/MOTO1718/DATATITU.dbf"):
        if registro["NROCHASIS"].strip() == numero_chasis.strip():
            return dict(registro)
    return None


def buscar_remito_entrega(nrochasis, ptoventa, remitoEntrega):
    # 1. Leer REMITOSX.DBF
    tabla_remitos = dbf.Table("D:/tiempo/vtiempo/GESTION/MOTO1718/REMITOSX.dbf")
    tabla_remitos.open(mode= dbf.READ_ONLY)

    cuenta = None
    for rec in tabla_remitos:
        if (int(rec.NROEST) == ptoventa and
            rec.NC == remitoEntrega):
            cuenta = rec.CUENTA
            break
    tabla_remitos.close()

    if not cuenta:
        print("Remito no encontrado")
        return

    # 2. Leer CTACTELIENT.DBF
    tabla_clientes = dbf.Table("D:/tiempo/vtiempo/GESTION/MOTO1718/CTACLIEN.dbf")
    tabla_clientes.open()

    datos_cliente = {}
    for rec in tabla_clientes:
        if rec.CNUMERO == cuenta:
            datos_cliente = {
                "TITULAR1": rec.CNOMBRE,
                "DOMICILIO1": rec.CDIREC,
                "LOCALIDAD1": rec.CLOCAL,
                "CODPOSTAL1": rec.CCP,
                "PROVINCIA1": rec.CPROVIN,
                "TIPODOC1": rec.TIPODOC,
                "NRODOC1": rec.NRODOC,
                "TELEFONO1": rec.TELEFONO,
            }
            break
    tabla_clientes.close()

    if not datos_cliente:
        print("Cliente no encontrado")
        return

    # 3. Insertar en DATATITU.DBF
    tabla_titular = dbf.Table("D:/tiempo/vtiempo/GESTION/MOTO1718/DATATITU.dbf")
    tabla_titular.open(mode=dbf.READ_WRITE)

    chasis_encontrado = False
    for record in tabla_titular:
        if record.NROCHASIS.strip() == nrochasis.strip():
            with record:
                for campo, valor in datos_cliente.items():
                    campo_mayus = campo.upper()
                    if campo_mayus in tabla_titular.field_names:
                        field_info = tabla_titular.field_info(campo_mayus)
                        if isinstance(valor, str):
                            max_len = field_info.length
                            if len(valor.encode('utf-8')) > max_len:
                                valor = valor[:max_len]  # Truncar si supera el límite
                        elif isinstance(valor, int):
                            # Validar tamaño del entero si es necesario
                            pass  # DBF maneja bien enteros en general si no superan el tamaño del campo
                        setattr(record, campo_mayus, valor)
            chasis_encontrado = True
            break

    tabla_titular.close()

    if not chasis_encontrado:
        print("No se encontró el número de chasis en DATATITU.dbf")

    # 4. Mostrar ventana con datos
    mostrar_datos_titulares(nrochasis, datos_cliente)




