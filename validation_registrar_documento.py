import arcpy

class ToolValidator(object):

    def __init__(self):
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        return

    def updateParameters(self):
        
        if self.params[8].value == "Original":
            self.params[9].enabled = False
        else:
            self.params[9].enabled = True
        
        if self.params[10].value == "Sin Geometria":
            self.params[11].enabled = False
        else:
            self.params[11].enabled = True
            
        return
    def updateMessages(self):
        registro_param = self.params[0]
        registro_ingresado = self.params[0].valueAsText
        existe_codigo = False
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
            if registro_ingresado is not None:
                existe_codigo = False
                with arcpy.da.SearchCursor(tabla_opiniones, ["op_reg"]) as cursor:
                    for fila in cursor:
                        if fila[0] == registro_ingresado:
                            existe_codigo = True
                            break
            
            if existe_codigo:
                registro_param.setErrorMessage("El codigo que intenta ingresar ya existe en la base de datos. Agregue un codigo diferente.")
                # Deshabilitar los parametros si el codigo existe menos el parametro [0]
                self.params[1].enabled = False
                self.params[2].enabled = False
                self.params[3].enabled = False
                self.params[4].enabled = False
                self.params[5].enabled = False
                self.params[6].enabled = False
                self.params[7].enabled = False
                self.params[8].enabled = False
                self.params[10].enabled = False
            else:
                # Habilitar los parametros si el codigo no existe
                self.params[1].enabled = True
                self.params[2].enabled = True
                self.params[3].enabled = True
                self.params[4].enabled = True
                self.params[5].enabled = True
                self.params[6].enabled = True
                self.params[7].enabled = True
                self.params[8].enabled = True
                self.params[10].enabled = True
    
        shapefile_param = self.params[11]
        if  shapefile_param.value:
            shapefile_path = shapefile_param.value
            desc = arcpy.Describe(shapefile_path)
            
            # Si el tipo de Geometria es punto
            if  desc.shapeType == "Point":
                fields = [field.name for field in arcpy.ListFields(shapefile_path)]
                if "op_este" not in fields or "op_norte" not in fields or "op_sect" not in fields or "op_nomb" not in fields  or "op_lati" not in fields or "op_long" not in fields:
                    shapefile_param.setErrorMessage("El Shapefile seleccionado debe contener las columnas 'op_este', 'op_norte', 'op_lati', 'op_long', 'op_sect' y/o 'op_nomb'.")
            
            # Si el tipo de Geometria es linea o poligono
            elif    desc.shapeType in ["Polyline", "Polygon"]:
                    fields = [field.name for field in arcpy.ListFields(shapefile_path)]
                    if "op_sect" not in fields or "op_nomb" not in fields:
                        shapefile_param.setErrorMessage("El Shapefile seleccionado debe contener las columnas 'op_sect' o 'op_nomb'.")
    
        # Verifica la coincidencia del tipo de parametro
        tipo_geometria_param = self.params[10].valueAsText
        if tipo_geometria_param == "Sin Geometria":
            self.params[10].clearMessage()
            self.params[11].value = None
        else:
            # Verificar si el tipo de geometria del paramametro esta seleccionado o no
            shapefile_param = self.params[11]
            if shapefile_param.value and tipo_geometria_param:
                shapefile_path = shapefile_param.value
                desc = arcpy.Describe(shapefile_path)
                tipo_geometria_shapefile = desc.shapeType

                # Convertir el tipo de Geometria a un termino comun si es necesario
                if tipo_geometria_shapefile == "Point":
                    tipo_geometria_shapefile = "Punto"
                elif tipo_geometria_shapefile == "Polyline":
                    tipo_geometria_shapefile = "Linea"
                elif tipo_geometria_shapefile == "Polygon":
                    tipo_geometria_shapefile = "Poligono"

                # Comparar y actualizar el mensaje de error si es necesario
                if tipo_geometria_param != tipo_geometria_shapefile:
                    shapefile_param.setErrorMessage("El tipo de geometria seleccionado ('{0}') no coincide con el tipo de geometria del shapefile ('{1}').".format(tipo_geometria_param, tipo_geometria_shapefile))
        return