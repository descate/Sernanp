import arcpy

class ToolValidator(object):

    def __init__(self):
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        return

    def updateParameters(self):
        return

    def updateMessages(self):
        # Definir ambas posibles rutas de conexiÃ³n
        db_path1 = r'Database Connections\SERNANP.sde\gdb.sde.Opiniones_Superposicion'
        db_path2 = r'Conexiones de base de datos\SERNANP.sde\gdb.sde.Opiniones_Superposicion'

        # Verificar la existencia de las bases de datos y seleccionar la correcta
        if arcpy.Exists(db_path1):
            tabla_opiniones = db_path1
        elif arcpy.Exists(db_path2):
            tabla_opiniones = db_path2
        else:
            # Manejar el caso en que ninguna base de datos exista
            tabla_opiniones = None
            print("Ninguna de las bases de datos especificadas estÃ¡ disponible.")
            
         # Continuar solo si se encontrÃ³ una tabla de opiniones vÃ¡lida
        if tabla_opiniones is not None:
            
            if self.params[0].altered:
                registro = self.params[0].value
                if registro is not None:
                    dbf_path = tabla_opiniones
                    existe_registro = False
                    with arcpy.da.SearchCursor(dbf_path, ["op_reg", "op_ref", "op_sol", "op_inst"]) as search_cursor:
                        for row in search_cursor:
                            if row[0] == registro:
                                existe_registro = True
                                mensaje = u"Registro encontrado:\n Documento de Referencia: '{}', \n Solicitante: '{}', \nInstitucion: '{}'".format(row[1], row[2], row[3])
                                self.params[0].setWarningMessage(mensaje)
                                break
                    if not existe_registro:
                        self.params[0].setErrorMessage("El codigo de registro '{}' no existe en la tabla DBF.".format(registro))
            return