############################################################################################
# TITLE        : HRU_PARSE
# CREATED BY   : Charmaine Bonifacio
# DATE CREATED : June 30, 2014
# EDITED BY    : Charmaine Bonifacio
# DATE EDITED  : June 30, 2014
#------------------------------------------------------------------------------------------
# DESCRIPTION  : This python script will run parse out the GRIDCODE field.
#------------------------------------------------------------------------------------------
# INPUT        : <> The Daily 10KM Grid Data
#                <> RCM Grid Data
#                <> Monthly Raster File per variable (ie Tmin, Tmax or Precip)
# OUTPUT       : <> Create an input folder that contains the following:
#                   <> Two shapefiles: AB10 and RCM.
#                <> Create an processed folder that contains the following:
#                   <> 36 .DBF files for AB
#                   <> 36 .DBF files for RCM
#                   <> 36 .SHP files for each union
#                <> Create an output folder that contains the following:
#                   <> 36 .DBF files with only required fields.
############################################################################################

# Import system modules
import os
import sys
import arcpy
import arcpy.sa as sa
from arcpy import env
from arcpy.sa import *
import time
import math

# Set overwrite option
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# GLOBAL VARIABLES
global ignore_nodata 
global statistics_type
global statistics_area
global statistics_count
global join_type
global join_attributes 
global cluster_tolerance 
global gaps
global selection_type
global field_name
global field_type 
global field_precision 
global field_scale 
global field_length 
global field_alias 
global field_is_nullable 
global field_is_required 
global field_domain
global expression_type
global code_block

# Function Parameters for GEOPROCESSING
ignore_nodata = "DATA"
statistics_type = "MEAN"
statistics_area = "AREA"
statistics_count = "COUNT"
join_type = "KEEP_ALL"
join_attributes = "ALL"
cluster_tolerance = ""
gaps = "GAPS"
selection_type = "NEW_SELECTION"

# Function Parameters for TABLE
field_type = "DOUBLE"
field_precision = ""
field_scale = ""
field_length = ""
field_alias = ""
field_is_nullable = "NULLABLE"
field_is_required = "NON_REQUIRED"
field_domain = ""
expression_type = "VB"
code_block = "#"

# File Variables
global fileType
global dbfExt
global shpExt
dbfExt = '.dbf'
shpExt = '.shp'

############################################################################################                      
# HELPER FUNCTIONS
#-------------------------------------------------------------------------------------------
# FUNCTION: checkFolderStatus
# This function will check the status of the directory.
def checkFolderStatus( directoryPath ):
    print "Checking directory status on: "
    print "* %s " % directoryPath
    if os.path.exists(directoryPath) == True:
        print "Valid directory."
        return True
    else:
        print "Invalid directory. Try again."
        return False
#-------------------------------------------------------------------------------------------
# FUNCTION: createOutputFolder
# This function creates a directory if it does not exists.
def createOutputFolder( directoryPath ):
    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)
        print "Created output %s. " % directoryPath
    else: print "%s already exists. " % directoryPath
#-------------------------------------------------------------------------------------------
# FUNCTION: checkFileStatus
# This function checks the status of the file.
def checkFileStatus( fileName ):
    print "Checking file status on: "
    print "* %s " % fileName
    if os.path.isfile(fileName) == True:
        print "Valid input. File exists."
        return True
    else:
        print "Invalid input. File does not exist."
        return False
#-------------------------------------------------------------------------------------------
# FUNCTION: concatenateStringNames
# This function renames the field names by concatenating two strings and a link.
def renameStrings( name1, name2, link ):
    return name1 + link + name2
#-------------------------------------------------------------------------------------------
# FUNCTION: quitProgram
# User is required to enter "O" to quit the program
def quitProgram():
    global quitText
    quitText = input("\nEnter 0 to quit program: ")
    if quitText == 0:
        return True
    else: quitProgram();
    
############################################################################################
# GEOPROCESSING FUNCTIONS
#-------------------------------------------------------------------------------------------
# FUNCTION: zonaltable_joinfieldManagement
#   This function calculates zonal statistics on the input and creates an output .DBF file.
#   The output is then permanently joined with the input file.
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       ZonalStatisticsAsTable (in_zone_data, zone_field, in_value_raster, out_table,
#                               {ignore_nodata}, {statistics_type})
#       JoinField_management (in_data, in_field, join_table, join_field,
#                             {fields})
def zonaltable_joinfieldManagement( workspace, in_zone_data,
                                   in_value_raster, out_table, field ):
    env.workspace = workspace
    arcpy.sa.ZonalStatisticsAsTable(in_zone_data,
                                       field,
                                       in_value_raster,
                                       out_table,
                                       ignore_nodata,
                                       statistics_type)
    fieldList = [statistics_count, statistics_type]
    arcpy.JoinField_management(in_zone_data,
                               field,
                               out_table,
                               field,
                               fieldList)
#-------------------------------------------------------------------------------------------
# FUNCTION: unionAnalysis
#   This function will union any number of input features.
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       Union_analysis (in_features, out_feature_class,
#                       {join_attributes}, {cluster_tolerance}, {gaps})
def unionAnalysis( workspace, in_features, out_feature_class ):
    env.workspace = workspace
    arcpy.Union_analysis(in_features,
                         out_feature_class,
                         join_attributes,
                         cluster_tolerance,
                         gaps)
#-------------------------------------------------------------------------------------------
# FUNCTION: selectdelete_Management
#
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       SelectLayerByAttribute_management (in_layer_or_view,
#                                          {selection_type}, {where_clause})
def selectdelete_Management( in_layer_or_view, selectionClause ):
    arcpy.SelectLayerByAttribute_management(in_layer_or_view,
                                            selection_type,
                                            selectionClause)
    arcpy.DeleteRows_management(in_layer_or_view)
#-------------------------------------------------------------------------------------------
# FUNCTION: addcalculate_FieldManagement
#
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       AddField_management (in_table, field_name, field_type,
#                            {field_precision}, {field_scale}, {field_length},
#                            {field_alias}, {field_is_nullable},
#                            {field_is_required}, {field_domain})
#       CalculateField_management (in_table, field_name, expression,
#                                  {expression_type}, {code_block})
def addcalculate_FieldManagement( workspace, in_table, field_name,
                                 in_field_type, expression ):
    env.workspace = workspace
    arcpy.AddField_management(in_table,
                              field_name,
                              in_field_type,
                              field_precision,
                              field_scale,
                              field_length,
                              field_alias,
                              field_is_nullable,
                              field_is_required,
                              field_domain)
    arcpy.CalculateField_management(in_table,
                                    field_name,
                                    expression,
                                    expression_type)
#-------------------------------------------------------------------------------------------
# FUNCTION: copyBaseFiles
#   This function copies the original feature dataset and saves it as a new feature dataset.
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       CopyFeatures_management (in_features, out_feature_class,
#                                {config_keyword}, {spatial_grid_1},
#                                 {spatial_grid_2}, {spatial_grid_3})
def copyBasefiles( workspace, in_feature, out_feature ):
    env.workspace = workspace
    arcpy.CopyFeatures_management(in_feature,
                                  os.path.join(workspace, out_feature))
#-------------------------------------------------------------------------------------------
# FUNCTION: copyTable
#   This function converts the input table to a dBase table.
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       TableToTable_conversion (in_rows, out_path, out_name,
#                                {where_clause}, {field_mapping}, {config_keyword})
def copyTable ( workspace, in_table, out_table ):
    env.workspace = workspace
    arcpy.TableToTable_conversion(in_table, workspace, out_table)
#-------------------------------------------------------------------------------------------
# FUNCTION: deleteFields_FieldManagement
#   This function deletes unnecessary fields using a list.
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       DeleteField_management (in_table, drop_field)
def deleteFields_FieldManagement( workspace, in_table, drop_field ):
    env.workspace = workspace
    field_list = arcpy.ListFields(in_table)
    # Populate list of fields in the feature dataset
    listx = []
    for field in field_list:
        listx.append(field.name)
    # Remove required fields for the summary table
    for reqField in drop_field:
        if reqField in listx:
            listx.remove(reqField)
    arcpy.DeleteField_management(in_table, listx)
    
############################################################################################
# MAIN FUNCTION
#-------------------------------------------------------------------------------------------
def main():
    # Obtain Input From User
    workSpace = r"C:\test\hru\7\ICELLN"       # OUTPUT Directory
    #
    # Monitor Time Elapsed
    # ===================================
    beginTime = time.clock()
    print ("\nChecking files and directories")
    #
    # List Classes
    # ===================================
    env.workspace = workSpace
    count = 0
    featureList = arcpy.ListFeatureClasses()
    for fc in featureList:
        count += 1
    record_count = int(count)
    if record_count == 0:
        raise ValueError("There are {0} features found within the directory".format(record_count))
    print ("\nNumber of feature classes = {0}".format(record_count))
    #
    # Start Geoprocessing
    # ===================================
    env.workspace = workSpace
    featureList = arcpy.ListFeatureClasses()
    for fc in featureList:
        env.workspace = workSpace
        if arcpy.Exists( fc ) == True: 
            print ("Currently processing {} feature file.".format(fc))       
            # Add Fields: WS_ID, GRID_ID, ELEV_ID, LC_ID and SR_ID
            wsField = "WS_ID"
            expression = "Left([GRIDCODE],1)"
            addcalculate_FieldManagement( workSpace,
                                          fc,
                                          wsField,
                                          field_type,
                                          expression );
            gridField = "GRID_ID"
            expression = "Mid([GRIDCODE],2,3)"
            addcalculate_FieldManagement( workSpace,
                                          fc,
                                          gridField,
                                          field_type,
                                          expression );
            elevField = "ELEV_ID"
            expression = "Mid([GRIDCODE],5,2)"
            addcalculate_FieldManagement( workSpace,
                                          fc,
                                          elevField,
                                          field_type,
                                          expression );
            lcField = "LC_ID"
            expression = "Mid([GRIDCODE],7,2)"
            addcalculate_FieldManagement( workSpace,
                                          fc,
                                          lcField,
                                          field_type,
                                          expression );
            srField = "SR_ID"
            expression = "Right([GRIDCODE],1)"
            addcalculate_FieldManagement( workSpace,
                                          fc,
                                          srField,
                                          field_type,
                                          expression );
            
    endTime = time.clock()
    print ("Elapsed Time: {}\n".format(endTime - beginTime))
    quitProgram();
    return True # For MAIN function
        
#############################################################################################
# RUN MAIN PYTHON SCRIPT
#--------------------------------------------------------------------------------------------
try:
    if main() == False: sys.exit(0);

except:
    print arcpy.GetMessages()

