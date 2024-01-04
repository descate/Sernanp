# -*- coding: utf-8 -*-
import arcpy
import tempfile
import tkinter as tk
from tkinter import filedialog
import tkFileDialog 
from PIL import Image, ImageTk
from tkinter import messagebox



# Establece la geodatabase de destino (SDE) con la codificación UTF-8
sde_connection = r'Database Connections\Connection to 10.10.14.38.sde'

# Establece la ruta completa a tu feature class en la geodatabase SDE con tildes
anp = u'Database Connections\SERNANP.sde\gdb.sde.ÁreasNaturalesProtegidasEstablecidas\gdb.sde.ANPAdministracionNacionalDefinitivas'
zr = u'Database Connections\SERNANP.sde\gdb.sde.ÁreasNaturalesProtegidasEstablecidas\gdb.sde.ANPAdministracionNacionalTransitorias'
zonificacion = u'Database Connections\SERNANP.sde\gdb.sde.ZonificaciónANP\gdb.sde.ZonificacionANP'
monitoreo_grillas = u'Database Connections\SERNANP.sde\gdb.sde.MonitoreoCobertura\gdb.sde.MonitoreoGrillas'
exa = u'Database Connections\SERNANP.sde\gdb.sde.MonitoreoANP\gdb.sde.EfectosActividadesIITrimestre2023'
# Establece la ruta al shapefile en el disco D con tildes
#shapefile_d = u'D:\ATD_PNCB_17092023_al_30092023_JOEL_V3.shp'


# Crea una ruta de archivo temporal para el resultado de la intersección
temp_dir = tempfile.gettempdir()  # Obtiene la carpeta temporal del sistema
intersect_monitoreo_anp = arcpy.CreateUniqueName("intersect_monitoreo_anp.shp", temp_dir)
intersect_monitoreo_anp_zoni = arcpy.CreateUniqueName("intersect_monitoreo_anp_zoni.shp", temp_dir) 
erase_monitoreo_anp_zoni = arcpy.CreateUniqueName("erase_monitoreo_anp_zoni.shp", temp_dir)
merge_monitoreo_anp_zoni = arcpy.CreateUniqueName("merged_monitoreo_anp_zoni.shp", temp_dir)
intersect_monitoreo_anp_zoni_grillas = arcpy.CreateUniqueName("intersect_monitoreo_anp_zoni_grillas.shp", temp_dir)
intersect_monitoreo_anp_zoni_grillas_exa = arcpy.CreateUniqueName("intersect_monitoreo_anp_zoni_grillas_exa.shp", temp_dir)
erase_monitoreo_anp_zoni_grillas_exa = arcpy.CreateUniqueName("erase_monitoreo_anp_zoni_grillas_exa.shp", temp_dir)
merge_monitoreo_anp_zoni_grillas_exa = arcpy.CreateUniqueName("merge_monitoreo_anp_zoni_grillas_exa.shp", temp_dir)

intersect_monitoreo_zr = arcpy.CreateUniqueName("intersect_monitoreo_zr.shp", temp_dir)
intersect_monitoreo_zr_grillas = arcpy.CreateUniqueName("intersect_monitoreo_zr_grillas.shp", temp_dir)
intersect_monitoreo_zr_grillas_exa = arcpy.CreateUniqueName("intersect_monitoreo_zr_grillas_exa.shp", temp_dir)
erase_monitoreo_zr_grillas_exa = arcpy.CreateUniqueName("erase_monitoreo_zr_grillas_exa.shp", temp_dir)
merge_monitoreo_zr_grillas_exa = arcpy.CreateUniqueName("merge_monitoreo_zr_grillas_exa.shp", temp_dir)

merge_monitoreo_anp_zr = arcpy.CreateUniqueName("merge_monitoreo_anp_zr.shp", temp_dir)

# Copiar los datos de 'anp_codi_1' al campo 'anp_codi'
expression_anp = "!anp_codi_1!"  # Esta expresión copiará los valores de 'anp_codi_1' a 'anp_codi'
expression_zoni = "!z_tipo!" #Esta expresión copiará los valores de
expression_grilla = "!zi_codi_1!"
expression_exa = "!columna_fi!"

# Ruta al shapefile permanente
ruta_shapefile_permanente = r'D:\Monitoreo_Planet_20231062.shp'

def seleccionar_shapefile():
    shapefile_path = tkFileDialog.askopenfilename(
        filetypes=[("Shapefiles", "*.shp"), ("Todos los archivos", "*.*")]
    )
    # Haz algo con la ruta del shapefile seleccionado
    # Muestra la ruta del shapefile seleccionado en la caja de texto
    caja_texto_shapefile.delete(0, tk.END)  # Limpia el contenido actual
    caja_texto_shapefile.insert(0, shapefile_path)
        
def validar_alertas():
    
    # Verifica si la caja de texto está vacía
    shapefile_path = caja_texto_shapefile.get()
    if not shapefile_path:
        messagebox.showwarning("Advertencia", "Debes seleccionar un shapefile antes de validar.")
        return  # Salimos de la función si la caja de texto está vacía
    arcpy.Intersect_analysis([shapefile_path, anp], intersect_monitoreo_anp)

    # Realizar el cálculo de campo
    arcpy.CalculateField_management(intersect_monitoreo_anp, "anp_codi", expression_anp, "PYTHON")

    # Lista de campos a eliminar
    campos_a_eliminar_anp = ["st_length1", "st_area__1", "anp_sigla", "anp_wdpaid", "last_edi_3","last_edi_2","created__2","created__1",
                        "anp_fecreg", "anp_docreg", "g_obs", "anp_felem", "anp_balem", "anp_felec", "anp_balec", "anp_uicn", "anp_suleg",
                        "anp_ubpo", "anp_sect", "anp_nomb", "anp_codi_1", "anp_cate", "FID_ANPAdm", "Shape_Area", "Shape_Le_1", "Shape_Leng",
                        "st_length_", "st_area_sh", "last_edi_1", "last_edite", "created_da", "created_us", "OBJECTID_2", "OBJECTID_1",
                        "FID_monito"]

    # Eliminar los campos
    for campo in campos_a_eliminar_anp:
        arcpy.DeleteField_management(intersect_monitoreo_anp, campo)
        
    arcpy.Intersect_analysis([intersect_monitoreo_anp,zonificacion], intersect_monitoreo_anp_zoni)


    arcpy.CalculateField_management(intersect_monitoreo_anp_zoni, "md_zonif", expression_zoni, "PYTHON")

    # Obtener la lista de campos del shapefile
    field_list = [field.name for field in arcpy.ListFields(intersect_monitoreo_anp_zoni)]

    # Identificar los 10 últimos campos
    last_21_fields = field_list[-21:]

    # Agregar "FID_monito" a la lista de campos a eliminar si no se encuentra en los últimos 10 campos
    campos_a_eliminar = last_21_fields + ["FID_monito","FID_inters"]

    # Eliminar los campos
    for campo in campos_a_eliminar:
        arcpy.DeleteField_management(intersect_monitoreo_anp_zoni, campo)
        


    # Realiza la operación de Erase
    arcpy.Erase_analysis(intersect_monitoreo_anp, intersect_monitoreo_anp_zoni, erase_monitoreo_anp_zoni)

    # Realiza la operación de fusión
    arcpy.Merge_management([intersect_monitoreo_anp_zoni, erase_monitoreo_anp_zoni], merge_monitoreo_anp_zoni)


    arcpy.Intersect_analysis([merge_monitoreo_anp_zoni, monitoreo_grillas], intersect_monitoreo_anp_zoni_grillas)

    arcpy.CalculateField_management(intersect_monitoreo_anp_zoni_grillas, "zi_codi", expression_grilla, "PYTHON")

    # Obtener la lista de campos del shapefile
    field_list2 = [field.name for field in arcpy.ListFields(intersect_monitoreo_anp_zoni_grillas)]

    # Identificar los 10 últimos campos
    last_14_fields = field_list2[-14:]

    # Agregar "FID_monito" a la lista de campos a eliminar si no se encuentra en los últimos 10 campos
    campos_a_eliminar2 = last_14_fields + ["FID_inters","FID_merged"]

    # Eliminar los campos
    for campo in campos_a_eliminar2:
        arcpy.DeleteField_management(intersect_monitoreo_anp_zoni_grillas, campo)
        
    arcpy.Intersect_analysis([intersect_monitoreo_anp_zoni_grillas,exa], intersect_monitoreo_anp_zoni_grillas_exa)

    arcpy.CalculateField_management(intersect_monitoreo_anp_zoni_grillas_exa, "md_exa", expression_exa, "PYTHON")

    # Obtener la lista de campos del shapefile
    field_list3 = [field.name for field in arcpy.ListFields(intersect_monitoreo_anp_zoni_grillas_exa)]

    # Identificar los 10 últimos campos
    last_95_fields = field_list3[-95:]

    # Agregar "FID_monito" a la lista de campos a eliminar si no se encuentra en los últimos 10 campos
    campos_a_eliminar3 = last_95_fields + ["FID_inters"]

    # Eliminar los campos
    for campo in campos_a_eliminar3:
        arcpy.DeleteField_management(intersect_monitoreo_anp_zoni_grillas_exa, campo)

    # Realiza la operación de Erase
    arcpy.Erase_analysis(intersect_monitoreo_anp_zoni_grillas, intersect_monitoreo_anp_zoni_grillas_exa, erase_monitoreo_anp_zoni_grillas_exa)

    arcpy.Merge_management([intersect_monitoreo_anp_zoni_grillas_exa, erase_monitoreo_anp_zoni_grillas_exa], merge_monitoreo_anp_zoni_grillas_exa)


    #############################################################################################################################

    arcpy.Intersect_analysis([shapefile_path, zr], intersect_monitoreo_zr)
    
    #Realizar el cálculo de campo
    arcpy.CalculateField_management(intersect_monitoreo_zr, "anp_codi", expression_anp, "PYTHON")

    # Obtener la lista de campos del shapefile
    field_list = [field.name for field in arcpy.ListFields(intersect_monitoreo_zr)]

    # Identificar los 10 últimos campos
    last_25_fields = field_list[-25:]

    # Agregar "FID_monito" a la lista de campos a eliminar si no se encuentra en los últimos 10 campos
    campos_a_eliminar4 = last_25_fields + ["FID_Monito"]

    # Eliminar los campos
    for campo in campos_a_eliminar4:
        arcpy.DeleteField_management(intersect_monitoreo_zr, campo)

    arcpy.Intersect_analysis([intersect_monitoreo_zr, monitoreo_grillas], intersect_monitoreo_zr_grillas)

    arcpy.CalculateField_management(intersect_monitoreo_zr_grillas, "zi_codi", expression_grilla, "PYTHON")

    # Obtener la lista de campos del shapefile
    field_list = [field.name for field in arcpy.ListFields(intersect_monitoreo_zr_grillas)]

    # Identificar los 10 últimos campos
    last_14_fields2 = field_list[-14:]

    # Agregar "FID_monito" a la lista de campos a eliminar si no se encuentra en los últimos 10 campos
    campos_a_eliminar5 = last_14_fields2 + ["FID_inters"]

    # Eliminar los campos
    for campo in campos_a_eliminar5:
        arcpy.DeleteField_management(intersect_monitoreo_zr_grillas, campo)
        
    arcpy.Intersect_analysis([intersect_monitoreo_zr_grillas, exa], intersect_monitoreo_zr_grillas_exa)# Obtener la lista de campos del shapefile

    arcpy.CalculateField_management(intersect_monitoreo_zr_grillas_exa, "md_exa", expression_exa, "PYTHON")

    field_list = [field.name for field in arcpy.ListFields(intersect_monitoreo_zr_grillas_exa)]

    # Identificar los 10 últimos campos
    last_95_fields2 = field_list[-95:]

    # Agregar "FID_monito" a la lista de campos a eliminar si no se encuentra en los últimos 10 campos
    campos_a_eliminar6 = last_95_fields2 + ["FID_inters"]

    # Eliminar los campos
    for campo in campos_a_eliminar6:
        arcpy.DeleteField_management(intersect_monitoreo_zr_grillas_exa, campo)

    arcpy.Erase_analysis(intersect_monitoreo_zr_grillas, intersect_monitoreo_zr_grillas_exa, erase_monitoreo_zr_grillas_exa)

    arcpy.Merge_management([intersect_monitoreo_zr_grillas_exa, erase_monitoreo_zr_grillas_exa], merge_monitoreo_zr_grillas_exa)

    arcpy.Merge_management([merge_monitoreo_anp_zoni_grillas_exa, merge_monitoreo_zr_grillas_exa], merge_monitoreo_anp_zr)
    
    """ # Define una expresión para utilizar el valor de mes_reporte en el cálculo del campo
    expression_mes_rep = '"' + mes_reporte + '"'  # Debe estar entre comillas

     # Actualiza el campo "md_mesrep" con el valor de mes_reporte en el shapefile final
    arcpy.CalculateField_management(merge_monitoreo_anp_zr, "md_mesrep", expression_mes_rep, "PYTHON") """

    #############################################################################################################################
    # Copiar el shapefile temporal a uno permanente
    arcpy.CopyFeatures_management(merge_monitoreo_anp_zr, ruta_shapefile_permanente)


    # Imprimir un mensaje de éxito
    # Imprime un mensaje de finalización
    print("Operacion de interseccion completada con exito.")
    print("Shapefile temporal exportado a uno permanente con éxito.")

def seleccionar_ruta_shapefile_permanente():
    ruta = filedialog.asksaveasfilename(defaultextension=".shp", filetypes=[("Shapefile", "*.shp")])
    caja_texto_ruta.delete(0, tk.END)  # Limpia el contenido actual
    caja_texto_ruta.insert(0, ruta)
    
# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Validación de Alertas")
ventana.geometry("600x150")
# Carga la imagen que deseas usar como icono (asegúrate de ajustar la ruta a tu imagen)
icono_imagen = Image.open("C:\Program Files (x86)\ArcGIS\Desktop10.8\\bin\Icons\Folder16.png")
icono = ImageTk.PhotoImage(icono_imagen)

etiqueta_shapefile = tk.Label(ventana, text="Seleccione el Shapefile:")
etiqueta_shapefile.grid(row=0, column=0, padx=10, pady=0, sticky='w')

caja_texto_shapefile = tk.Entry(ventana, width=90)
caja_texto_shapefile.grid(row=1, column=0, padx=10, pady=0)

boton_seleccionar_shapefile = tk.Button(ventana, image=icono, command=seleccionar_shapefile)
boton_seleccionar_shapefile.grid(row=1, column=1, padx=5, pady=0)

# Agregar un campo de texto para mostrar la ruta seleccionada
etiqueta_ruta = tk.Label(ventana, text="Ruta del Shapefile Permanente:")
etiqueta_ruta.grid(row=2, column=0, padx=10, pady=0)

caja_texto_ruta = tk.Entry(ventana, width=90)
caja_texto_ruta.grid(row=3, column=0, padx=10, pady=0)

# Agregar un botón para seleccionar la ruta
boton_seleccionar_ruta = tk.Button(ventana, text="Seleccionar Ruta", command=seleccionar_ruta_shapefile_permanente)
boton_seleccionar_ruta.grid(row=3, column=1, padx=5, pady=0)

boton_interseccion = tk.Button(ventana, text="Validar Alertas", command=validar_alertas)
boton_interseccion.grid(row=3, column=0, padx=10, pady=20, columnspan=2)

ventana.mainloop()