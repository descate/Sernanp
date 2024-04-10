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

registro = arcpy.GetParameter(0)
fecha_respuesta = arcpy.GetParameter(1)
informe_respuesta = arcpy.GetParameter(2)
tipo_documento = arcpy.GetParameter(3)
documento_respuesta = arcpy.GetParameter(4)
superposicion_anp = arcpy.GetParameter(5)
superposicion_acr = arcpy.GetParameter(6)
superposicion_acp = arcpy.GetParameter(7)
superposicion_zr = arcpy.GetParameter(8)
tabla_dbf = 'gdb.sde.Opiniones_Superposicion'
dbf_path = os.path.join(gdb_path, tabla_dbf)

def modificar_datos(registro, fecha_respuesta, informe_respuesta, tipo_documento, documento_respuesta,
                    superposicion_anp, superposicion_acr, superposicion_acp, superposicion_zr):
    intentos_maximos = 3  
    intento_actual = 0  
    while intento_actual < intentos_maximos:
        try:
            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(with_undo=False, multiuser_mode=True)
            edit.startOperation()

            with arcpy.da.UpdateCursor(dbf_path, ["op_reg", "op_fecres", "op_infres", "op_tipdoc", "op_docres", "op_supanp", "op_supacr", "op_supacp", "op_supzr"]) as cursor:
                for row in cursor:
                    if row[0] == registro:
                        row[1] = fecha_respuesta
                        row[2] = informe_respuesta
                        row[3] = tipo_documento
                        row[4] = documento_respuesta
                        row[5] = superposicion_anp
                        row[6] = superposicion_acr
                        row[7] = superposicion_acp
                        row[8] = superposicion_zr
                        cursor.updateRow(row)
            edit.stopOperation()
            edit.stopEditing(True)
            arcpy.AddMessage("Datos actualizados para el registro {}".format(registro))
            break

        except Exception as e:
            error_message = str(e)
            arcpy.AddMessage("Error al intentar registrar los datos: {}".format(error_message))
            intento_actual += 1 
        
        finally:
            if intento_actual >= intentos_maximos:
                arcpy.AddMessage("Se alcanzó el número máximo de intentos. No se pudo registrar los datos.")

modificar_datos(registro, fecha_respuesta, informe_respuesta, tipo_documento, documento_respuesta, 
                superposicion_anp, superposicion_acr, superposicion_acp, superposicion_zr)