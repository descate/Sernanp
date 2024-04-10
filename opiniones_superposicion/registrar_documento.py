# -*- coding: utf8 -*-
import arcpy
import os
import time

# Definir las posibles rutas de conexion
conexion1 = r'Database Connections\SERNANP.sde'  # Ruta que no existe
conexion2 = r'Conexiones de base de datos\SERNANP.sde'

# Funcion para verificar la conexion
def verificar_conexion(ruta):
    try:
        # Intentar abrir un dataset especifico o realizar una operacion de prueba
        # Cambiar "dataset_prueba" por el nombre de un dataset que sabes que debe existir
        test_path = ruta + '\\gdb.sde.OpinionesSuperposicion'  # Ajusta segun la estructura de tu base de datos
        if arcpy.Exists(test_path):
            arcpy.AddMessage("Conexion exitosa a {}".format(ruta))
            return True
        else:
            arcpy.AddMessage("Fallo al conectar a {}. Dataset de prueba no encontrado.".format(ruta))
            return False
    except:
        arcpy.AddMessage("Fallo al conectar a {}".format(ruta))
        return False

# Intentar conectar a las bases de datos en orden
if verificar_conexion(conexion1):
    gdb_path = conexion1
elif verificar_conexion(conexion2):
    gdb_path = conexion2
else:
    arcpy.AddMessage("No se pudo establecer conexión con las bases de datos.")
    
arcpy.env.workspace = gdb_path

shapefile_path = None

registro = arcpy.GetParameter(0)
fecha_registro = arcpy.GetParameter(1)
nombre_solicitante = arcpy.GetParameter(2)
cargo = arcpy.GetParameter(3)
nombre_institucion = arcpy.GetParameter(4)
correo_electronico = arcpy.GetParameter(5)
documento_referencia = arcpy.GetParameter(6)
nombre_consulta = arcpy.GetParameter(7)
tipo_registro = arcpy.GetParameter(8)
antecedente = arcpy.GetParameter(9)
tipo_geometria = arcpy.GetParameter(10)
shapefile_path = arcpy.GetParameter(11)
tabla_dbf = 'gdb.sde.Opiniones_Superposicion'
dbf_path = os.path.join(gdb_path, tabla_dbf)

def guardar_datos(registro, fecha_registro, nombre_solicitante, cargo, nombre_institucion, correo_electronico,
                  documento_referencia, nombre_consulta, tipo_registro, antecedente):
    intentos_maximos = 3  
    intento_actual = 0  
    while intento_actual < intentos_maximos:
        try:
            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(with_undo=False, multiuser_mode=True)
            edit.startOperation()

            with arcpy.da.InsertCursor(dbf_path, 
                                       ["op_reg", "op_fecreg", "op_sol", "op_car", "op_inst", "op_email",
                                        "op_ref", "op_nomcon", "op_tipreg", "op_regant"]) as cursor:
                cursor.insertRow((registro, fecha_registro, nombre_solicitante, cargo, nombre_institucion,
                                  correo_electronico, documento_referencia, nombre_consulta, tipo_registro, antecedente))

            edit.stopOperation()
            edit.stopEditing(True)
            arcpy.AddMessage("Datos registrados correctamente")
            break

        except Exception as e:
            error_message = str(e)
            arcpy.AddMessage("Error al intentar registrar los datos: {}".format(error_message))
            intento_actual += 1  # Incrementa el contador de intentos
            
            if "Function or procedure does not exist" in error_message:
                arcpy.AddMessage("Reintentando la operación...")
                time.sleep(2)  # Espera 2 segundos antes de reintentar
            else:
                arcpy.AddMessage("Error no relacionado con la existencia de la función o procedimiento. No se reintentará.")
                break  # Si el error no es el esperado, salir del bucle
        finally:
            # Este bloque se ejecuta tanto si se produce una excepción como si no se produce
            if intento_actual >= intentos_maximos:
                arcpy.AddMessage("Se alcanzó el número máximo de intentos. No se pudo registrar los datos.")

# Función para copiar datos al feature class según el tipo de geometría
def copiar_datos_feature_class(shapefile_path, registro):
    try:
        # Determina el tipo de geometría del shapefile
        desc = arcpy.Describe(shapefile_path)
        tipo_geometria = desc.shapeType  # 'Point', 'Polyline', 'Polygon'

        # Define los campos específicos según el tipo de geometría
        campos_comunes = ['op_sect', 'op_nomb']
        if tipo_geometria == 'Point':
            campos = ['SHAPE@XY'] + ['op_este', 'op_norte','op_lati','op_long'] + campos_comunes
            feature_class_destino = gdb_path + '\\gdb.sde.OpinionesSuperposicion\gdb.sde.OpinionesPuntos'
        elif tipo_geometria in ['Polyline', 'Polygon']:
            campos = ['SHAPE@'] + campos_comunes
            if tipo_geometria == 'Polyline':
                feature_class_destino = gdb_path + '\\gdb.sde.OpinionesSuperposicion\gdb.sde.OpinionesLineas'
            else:  # Polygon
                feature_class_destino = gdb_path + '\\gdb.sde.OpinionesSuperposicion\gdb.sde.OpinionesPoligonos'
        else:
            arcpy.AddError("Tipo de geometria no soportado.")
            return
        
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(with_undo=False, multiuser_mode=True)
        edit.startOperation()
        # Copia los datos al feature class correspondiente
        with arcpy.da.SearchCursor(shapefile_path, campos) as sCursor, \
            arcpy.da.InsertCursor(feature_class_destino, campos + ['op_reg']) as iCursor:
            for row in sCursor:
                # Convertir la tupla a lista para poder modificar los valores
                row_list = list(row)
                # Antes de insertar el valor, verificamos si es nulo o está en blanco
                for index in range(1, len(row_list)):  # Empezamos desde el segundo elemento, omitiendo el SHAPE@
                    if row_list[index] is None or row_list[index] == "":
                        # Si el valor es nulo o está en blanco, se puede asignar un valor predeterminado o realizar otra acción
                        row_list[index] = None
                # Convertir la lista de nuevo a tupla
                row = tuple(row_list)
                iCursor.insertRow(row + (registro,))
        edit.stopOperation()
        edit.stopEditing(True)
        arcpy.AddMessage("Datos registrados correctamente")
    except Exception as e:
        arcpy.AddMessage("Error: {}".format(str(e)))

# Llamar a la función con los valores proporcionados
guardar_datos(registro, fecha_registro, nombre_solicitante, cargo, nombre_institucion, correo_electronico,
              documento_referencia, nombre_consulta, tipo_registro, antecedente) 

# Llama a la función para copiar los datos al feature class correspondiente
if tipo_geometria != 'Sin Geometria':
    copiar_datos_feature_class(shapefile_path, registro)