import arcpy
class ToolValidator(object):


  def __init__(self):

    self.params = arcpy.GetParameterInfo()

  def initializeParameters(self):
    if self.params[0].altered:  
            values = set()
            fc_path = ur'Database Connections\SERNANP.sde\gdb.sde.\u00C1reasNaturalesProtegidasEstablecidas\gdb.sde.ANPAdministracionNacionalDefinitivas'
            with arcpy.da.SearchCursor(fc_path, ["anp_codi","anp_cate", "anp_nomb"]) as cursor:
                for row in cursor:
                    value = row[0] + " " + row[1] + " " + row[2]
                    values.add(value)
            value_list = sorted(values)
            self.params[0].filter.list = value_list
    return

  def updateParameters(self):

    return

  def updateMessages(self):

    return