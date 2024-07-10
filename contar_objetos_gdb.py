# -*- coding: utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8') # Establecer la codificación de caracteres predeterminada

import arcpy
from datetime import datetime
import pandas as pd

# Establece la geodatabase de entrada
gdb_path = r'Database Connections\SERNANP.sde'
arcpy.env.workspace = gdb_path

# Lista todas las entidades y tablas en la geodatabase
datasets = arcpy.ListDatasets(feature_type='feature') + ['']
tables = arcpy.ListTables()

# Lista para almacenar los registros encontrados
registro_encontrado = []

# Función para dividir el DataFrame en trozos más pequeños
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

# Cuenta los registros en cada dataset y sus feature classes
def df_registros_creados(fecha_i, fecha_f):
    fecha_inicial = datetime.strptime(fecha_i, '%Y-%m-%d')  # Convertir la cadena a un objeto datetime
    fecha_final = datetime.strptime(fecha_f, '%Y-%m-%d')
    for ds in datasets:
        if ds == "gdb.sde.MonitoreoANP":
            continue  # Saltar el dataset gdb.sde.MonitoreoANP
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            # Construir la ruta completa al feature class
            fc_path = u"{}\{}".format(ds, fc) if ds else fc  # Prefijo u para tratar la cadena como Unicode
            fc_path_encoded = fc_path.encode('utf-8')  # Codificar la cadena en UTF-8
            
            try:
                # Realiza un cursor de fecha
                with arcpy.da.SearchCursor(fc_path_encoded, ["created_date", "created_user", "last_edited_date", "last_edited_user"]) as cursor:
                    for row in cursor:
                        created_date = row[0]  # Fecha en el dataset
                        created_user = row[1]  # Usuario que creó el registro
                        last_edited_date = row[2]
                        last_edited_user = row[3]
                        if fecha_inicial <= created_date <= fecha_final:
                            registro_encontrado.append((ds, fc, created_date, created_user, last_edited_date, last_edited_user))
            except Exception as e:
                #print(u"Error al acceder al campo created_date en {}: {}".format(fc_path, e))
                continue

    # Cuenta los registros en cada tabla
    for table in tables:
        try:
            with arcpy.da.SearchCursor(table, ["created_date", "created_user", "last_edited_date", "last_edited_user"]) as cursor:
                for row in cursor:
                    created_date = row[0]
                    created_user = row[1]
                    last_edited_date = row[2]
                    last_edited_user = row[3]
                    if fecha_inicial <= created_date <= fecha_final:
                        registro_encontrado.append(("Tabla", table, created_date, created_user, last_edited_date, last_edited_user))
        except Exception as e:
            #print("Error al contar registros en la tabla {}: {}".format(table, str(e)))
            continue

    # Convertir la lista de tuplas a un DataFrame de pandas
    df = pd.DataFrame(registro_encontrado, columns=['Dataset', 'FeatureClass', 'Fecha_Registro', 'Usuario', 'Fecha_Modificacion', 'Usuario'])
    df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro']).dt.strftime('%Y-%m-%d')
    df['Fecha_Modificacion'] = pd.to_datetime(df['Fecha_Modificacion']).dt.strftime('%Y-%m-%d')

    return(df)

def df_registros_modificados(fecha_i, fecha_f):
    fecha_inicial = datetime.strptime(fecha_i, '%Y-%m-%d')  # Convertir la cadena a un objeto datetime
    fecha_final = datetime.strptime(fecha_f, '%Y-%m-%d')
    for ds in datasets:
        if ds == "gdb.sde.MonitoreoANP":
            continue  # Saltar el dataset gdb.sde.MonitoreoANP
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            # Construir la ruta completa al feature class
            fc_path = u"{}\{}".format(ds, fc) if ds else fc  # Prefijo u para tratar la cadena como Unicode
            fc_path_encoded = fc_path.encode('utf-8')  # Codificar la cadena en UTF-8
            
            try:
                # Realiza un cursor de fecha
                with arcpy.da.SearchCursor(fc_path_encoded, ["created_date", "created_user", "last_edited_date", "last_edited_user"]) as cursor:
                    for row in cursor:
                        created_date = row[0]  # Fecha en el dataset
                        created_user = row[1]  # Usuario que creó el registro
                        last_edited_date = row[2]
                        last_edited_user = row[3]
                        if fecha_inicial <= last_edited_date <= fecha_final:
                            registro_encontrado.append((ds, fc, created_date, created_user, last_edited_date, last_edited_user))
            except Exception as e:
                #print(u"Error al acceder al campo created_date en {}: {}".format(fc_path, e))
                continue

    # Cuenta los registros en cada tabla
    for table in tables:
        try:
            with arcpy.da.SearchCursor(table, ["created_date", "created_user", "last_edited_date", "last_edited_user"]) as cursor:
                for row in cursor:
                    created_date = row[0]
                    created_user = row[1]
                    last_edited_date = row[2]
                    last_edited_user = row[3]
                    if fecha_inicial <= last_edited_date <= fecha_final:
                        registro_encontrado.append(("Tabla", table, created_date, created_user, last_edited_date, last_edited_user))
        except Exception as e:
            #print("Error al contar registros en la tabla {}: {}".format(table, str(e)))
            continue

    # Convertir la lista de tuplas a un DataFrame de pandas
    df = pd.DataFrame(registro_encontrado, columns=['Dataset', 'FeatureClass', 'Fecha_Registro', 'Usuario', 'Fecha_Modificacion', 'Usuario'])
    df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro']).dt.strftime('%Y-%m-%d')
    df['Fecha_Modificacion'] = pd.to_datetime(df['Fecha_Modificacion']).dt.strftime('%Y-%m-%d')
    df = df[df['Fecha_Registro'] != df['Fecha_Modificacion']]
    return(df)

# Escribir el DataFrame en el archivo Excel en una sola hoja
df_r_creados = df_registros_creados('2024-04-01','2024-06-30')
df_r_modificados = df_registros_modificados('2024-04-01','2024-06-30')

excel_writer_c = pd.ExcelWriter("registros_creados.xlsx", engine='openpyxl')
df_r_creados.to_excel(excel_writer_c, sheet_name='registros_creados', index=False)
excel_writer_c.save()

excel_writer_m = pd.ExcelWriter("registros_modificados.xlsx", engine='openpyxl')
df_r_modificados.to_excel(excel_writer_m, sheet_name='registros_modificados', index=False)
excel_writer_m.save()

print("Los registros encontrados han sido exportados a 'registros_encontrados.xlsx'.")