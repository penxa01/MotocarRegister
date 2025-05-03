from datetime import datetime

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
    from dbfread import DBF
    for registro in DBF("D:/tiempo/vtiempo/GESTION/MOTO1718/DATAMOTO.dbf"):
        if registro["NROCHASIS"].strip() == numero_chasis.strip():
            return dict(registro)
    return None

