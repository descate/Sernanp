# -*- coding: utf-8 -*-
import arcpy
import requests
import json
import pandas as pd
from shapely.geometry import MultiLineString
import os

# URL del archivo GeoJSON
url_geojson = 'https://sernanpperuconnect.smartconservationtools.org/server/noa/sharedlink/?uuid=2e5ba943-4eed-4ef3-827d-de2061482c57'

# Inicializa df fuera del bloque try
df = None

try:
    # Descargar el archivo GeoJSON desde la URL
    response = requests.get(url_geojson)
    
    # Verificar si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        geojson_data = json.loads(response.content.decode('utf-8'))

        # Crear listas para almacenar los atributos y geometrías
        datos = []
        geometrias = []

        # Iterar a través de las características (features) en el GeoJSON
        for feature in geojson_data['features']:
            # Obtener los atributos y la geometría de cada característica
            atributos = feature['properties']
            geometria = feature['geometry']

            # Crear un diccionario con los atributos y geometría
            fila = atributos.copy()
            fila['geometria'] = geometria  # Agregar la geometría como una nueva columna

            # Agregar la fila a la lista de datos
            datos.append(fila)

        # Convertir la lista de datos en un DataFrame de Pandas
        df = pd.DataFrame(datos)
    else:
        print("La solicitud no fue exitosa. Código de estado:", response.status_code)

except Exception as e:
    print("Ocurrió un error:", str(e))

# Eliminar registros con geometría vacía
df = df.dropna(subset=['geometria'])

# Crear una lista para almacenar las nuevas coordenadas
nuevas_coordenadas = []

# Iterar a través de las filas del DataFrame original
for index, row in df.iterrows():
    # Obtener las coordenadas de la geometría
    coordenadas = MultiLineString(row['geometria']['coordinates'])
    
    # Añadir las coordenadas a la lista
    nuevas_coordenadas.append(coordenadas)

# Añadir la nueva columna 'coordenadas' al DataFrame original
df['coordenadas'] = nuevas_coordenadas

df['anp_codi'] = 'RN06'
mapeo_mandate = {
    "Especial": 1,
    "Especial con fines de Intervención": 2,
    "Rutinario": 3,
    "Sobrevuelo": 4,
    "Vigilancia Comunal": 5,
    "Vigilancia en el PVC": 6
}
df['mandato'] = df['Mandate'].map(mapeo_mandate)

mapeo_transporte = {
    "Air": 1,
    "Ground": 2,
    "Water": 3,
}
df['transporte'] = df['Type'].map(mapeo_transporte)
# Imprimir el DataFrame actualizado

sistema_coordenada = arcpy.SpatialReference(32718)

registros_con_geometria = []

for index, row in df.iterrows():
    
    registro = (
        row['anp_codi'], row['Patrol_ID'], row['Patrol_Start_Date'], row['Patrol_End_Date'], row['transporte'],
        row['mandato'], row['Station'], row['Team'], row['Objective'], row['Patrol_Leg_ID'], row['Patrol_Leg_Start_Date'],
        row['Patrol_Leg_End_Date'], row['Patrol_Transport_Type'], row['Leader'], row['Pilot'],
        coordenadas# Agregar la geometria aqui
    )

    # Agregar el registro a la lista
    registros_con_geometria.append(registro)

print(df)


# Establecer la ruta de la geodatabase y el nombre del Feature Class
gdb_path = r'Database Connections\SERNANP.sde'
dataset = 'gdb.sde.VigilanciaControl'
feature_class_name = 'gdb.sde.Patrullaje'  # Reemplaza con el nombre deseado

# Combinar la ruta de la geodatabase con el nombre del Feature Class
fc = os.path.join(gdb_path, feature_class_name)

# Iniciar una sesion de edicion
edit = arcpy.da.Editor(r'Database Connections\SERNANP.sde')
edit.startEditing(False, True)  # Puedes ajustar los parametros segun tus necesidades

# Iniciar una operacion de edicion
edit.startOperation()

# Abrir un InsertCursor para insertar los registros en el Feature Class
with arcpy.da.InsertCursor(fc, ('anp_codi','pat_codi','pat_fecini','fecha','pat_tip','pat_mdt','pat_est','pat_sec', 'pat_obj', 'tra_cod','tra_fecini',
                                'tra_fecfin','tra_tip','tra_lid', 'tra_pil','SHAPE@')) as cursor:
    # Insertar las filas en el Feature Class
    for registro in registros_con_geometria:
        cursor.insertRow(registro)

# Confirma la operacion de edicion
edit.stopOperation()

# Finaliza la sesion de edicion (guardando los cambios)
edit.stopEditing(True)

print("Registros insertados exitosamente en el Feature Class.") 