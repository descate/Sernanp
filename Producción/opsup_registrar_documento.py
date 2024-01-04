# -*- coding: utf8 -*-
import arcpy

shapefile_path = None

registro = arcpy.GetParameter(0)
fecha_registro = arcpy.GetParameter(1)
nombre_solicitante = arcpy.GetParameter(2)
cargo = arcpy.GetParameter(3)
nombre_institucion = arcpy.GetParameter(4)
correo_electronico = arcpy.GetParameter(5)
documento_referencia = arcpy.GetParameter(6)
nombre_consulta = arcpy.GetParameter(7)
shapefile_path = arcpy.GetParameter(9)
coordenada_este = arcpy.GetParameter(10)
coordenada_norte = arcpy.GetParameter(11)
sector = arcpy.GetParameter(12)
nombre = arcpy.GetParameter(13)


# Ruta de la tabla DBF
dbf_path = r'D:\Geodatabases\gdb_opiniones_superposicion.gdb\Opiniones_Superposicion'

# Función para guardar los datos en la tabla DBF
def guardar_datos(registro, fecha_registro, nombre_solicitante, cargo, nombre_institucion, correo_electronico,
                  documento_referencia, nombre_consulta):
    try:
        # Utiliza arcpy para agregar los datos a la tabla DBF
        with arcpy.da.InsertCursor(dbf_path, ["sp_reg", "sp_fecreg", "sp_sol", "sp_car", "sp_inst", "sp_email",
                                             "sp_ref", "sp_nomcon"]) as cursor:
            cursor.insertRow((registro, fecha_registro, nombre_solicitante, cargo, nombre_institucion,
                              correo_electronico, documento_referencia, nombre_consulta))

        print("Datos registrados correctamente")

        global shapefile_path  # Accede a la variable global
        if shapefile_path:
            # Lista para almacenar todas las geometrías del shapefile
            geometrias_shapefile = []

            # Utiliza arcpy para leer todas las geometrías del shapefile
            with arcpy.da.SearchCursor(shapefile_path, ["SHAPE@"]) as search_cursor:
                for row in search_cursor:
                    geometrias_shapefile.append(row[0])

            # Tipo de geometría seleccionado
            tipo_geometria = arcpy.GetParameter(8)

            # Rutas de salida según el tipo de geometría
            if tipo_geometria == "Punto":
                output_feature_class_path = r'D:\Geodatabases\gdb_opiniones_superposicion.gdb\OpinionesSuperposicion\OpinionesPuntos'
            elif tipo_geometria == "Linea":
                output_feature_class_path = r'D:\Geodatabases\gdb_opiniones_superposicion.gdb\OpinionesSuperposicion\OpinionesLineas'
            elif tipo_geometria == "Poligono":
                output_feature_class_path = r'D:\Geodatabases\gdb_opiniones_superposicion.gdb\OpinionesSuperposicion\OpinionesPoligonos'
            else:
                print("No se seleccionó un tipo de geometría válido.")
                return

                        # Definir los campos comunes a todos los tipos de geometría
            campos_comunes = ["SHAPE@", "sp_reg", "sp_sector", "sp_nom"]

            # Añadir campos adicionales según el tipo de geometría
            if tipo_geometria == "Punto":
                campos_adicionales = ["sp_este", "sp_norte"]
            else:
                campos_adicionales = []

            # Combinar los campos comunes y adicionales
            campos_insert_cursor = campos_comunes + campos_adicionales

            # Utiliza arcpy para copiar las geometrías al feature class existente
            if geometrias_shapefile:
                with arcpy.da.InsertCursor(output_feature_class_path, campos_insert_cursor) as insert_cursor:
                    for geometry in geometrias_shapefile:
                        if tipo_geometria == "Punto":
                            insert_cursor.insertRow((geometry, registro, sector, nombre, coordenada_este, coordenada_norte))
                        elif tipo_geometria in ["Linea", "Poligono"]:
                            insert_cursor.insertRow((geometry, registro, sector, nombre))
                        else:
                            print("No se seleccionó un tipo de geometría válido.")
                            return

                print("Registros insertados en el feature class con la geometría del shapefile.")
            else:
                print("No se seleccionó un tipo de geometría válido.")

    except Exception as e:
        print("Error: {}".format(str(e)))

# Llamar a la función con los valores proporcionados
guardar_datos(registro, fecha_registro, nombre_solicitante, cargo, nombre_institucion, correo_electronico,
              documento_referencia, nombre_consulta)