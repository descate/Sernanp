import arcpy

# Ruta de la tabla DBF
dbf_path = r'D:\Geodatabases\gdb_opiniones_superposicion.gdb\Opiniones_Superposicion'

# Parámetro de entrada para el registro
registro = arcpy.GetParameter(0)

# Nuevos valores para los campos a modificar
nueva_fecha_respuesta = arcpy.GetParameter(1)
nuevo_informe_respuesta = arcpy.GetParameter(2)
nuevo_documento_respuesta = arcpy.GetParameter(3)

def modificar_datos(registro, nueva_fecha_respuesta, nuevo_informe_respuesta, nuevo_documento_respuesta):
    try:
        # Utiliza arcpy para verificar si el registro existe
        existe_registro = False
        with arcpy.da.SearchCursor(dbf_path, ["sp_reg"]) as search_cursor:
            for row in search_cursor:
                if row[0] == registro:
                    existe_registro = True
                    break

        if not existe_registro:
            arcpy.AddMessage("El registro {} no existe en la tabla. No se realizaron modificaciones.".format(registro))
            return

        # Utiliza arcpy para actualizar los datos en la tabla DBF
        with arcpy.da.UpdateCursor(dbf_path, ["sp_reg", "sp_fecres", "sp_infres", "sp_docres"]) as cursor:
            for row in cursor:
                if row[0] == registro:
                    row[1] = nueva_fecha_respuesta
                    row[2] = nuevo_informe_respuesta
                    row[3] = nuevo_documento_respuesta
                    cursor.updateRow(row)

        arcpy.AddMessage("Datos actualizados para el registro {}".format(registro))

    except Exception as e:
        arcpy.AddError("Error: {}".format(str(e)))

# Verificar si el registro existe antes de ejecutar la función
with arcpy.da.SearchCursor(dbf_path, ["sp_reg"]) as search_cursor:
    registros_existen = any(row[0] == registro for row in search_cursor)

if not registros_existen:
    arcpy.AddMessage("El registro {} no existe en la tabla. No se realizaron modificaciones.".format(registro))
else:
    # Llamar a la función con los nuevos valores
    modificar_datos(registro, nueva_fecha_respuesta, nuevo_informe_respuesta, nuevo_documento_respuesta)