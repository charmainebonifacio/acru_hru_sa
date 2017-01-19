############################################################################################
# TITLE        : HRU_DELINEATION
# CREATED BY   : Charmaine Bonifacio
# DATE CREATED : June 18, 2014
# EDITED BY    : Charmaine Bonifacio
# DATE EDITED  : June 20, 2014
#------------------------------------------------------------------------------------------
# DESCRIPTION  : This python script delineate hydrological response units based
#                on five input raster files.
#------------------------------------------------------------------------------------------
# INPUT        : <> The Daily 10KM Grid Data
#                <> RCM Grid Data
#                <> Monthly Raster File per
#                <> RCM Grid Data
#                <> Monthly Raster File per
# OUTPUT       : <> Create an output folder that contains the following:
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

# Function Parameters for RASTER CONVERSION
global simplify
global raster_field
simplify = "NO_SIMPLIFY"
raster_field = "Value"

# Function Parameters for DISSOLVE
global dissolve_field
global statistics_fields
global multi_part
global unsplit_lines
dissolve_field = "GRIDCODE"
statistics_fields = ""
multi_part = "MULTI_PART"
unsplit_lines = "DISSOLVE_LINES"

# Function Parameters for TABLE
global field_name
global field_type 
global field_precision 
global field_scale 
global field_length 
global field_alias 
global field_is_nullable 
global field_is_required 
global field_domain
global expression
global expression_type
global code_block
field_name = "AREAKM2"
field_type = "DOUBLE"
field_precision = ""
field_scale = ""
field_length = ""
field_alias = ""
field_is_nullable = "NULLABLE"
field_is_required = "NON_REQUIRED"
field_domain = ""
expression = "!SHAPE.AREA@SQUAREKILOMETERS!"
expression_type = "PYTHON_9.3"
code_block = "#"

# Miscellaneous variables:
global underScore
global output
underScore = "_"
output = "Results"

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
# FUNCTION: rasterConversion
#   RasterToPolygon_conversion (in_raster, out_polygon_features, {simplify}, {raster_field})
def rasterConversion( workspace, in_raster, out_polygon_features ):
    env.workspace = workspace
    arcpy.RasterToPolygon_conversion(in_raster,
                                     out_polygon_features,
                                     simplify,
                                     raster_field)
#-------------------------------------------------------------------------------------------
# FUNCTION: rasterConversion
#   Dissolve_management (in_features, out_feature_class, {dissolve_field},
#                        {statistics_fields}, {multi_part}, {unsplit_lines})
def dissolveManagement( workspace, in_features, out_feature_class, inputList ):
    env.workspace = workspace
    arcpy.Dissolve_management(in_features,
                        out_feature_class,
                        inputList,
                        statistics_fields,
                        multi_part,
                        unsplit_lines)
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
def addcalculate_FieldManagement( workspace, in_table  ):
    env.workspace = workspace
    arcpy.AddField_management(in_table,
                              field_name,
                              field_type,
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

############################################################################################
# MAIN FUNCTION
#-------------------------------------------------------------------------------------------
def main():
    # Obtain Input From User
    ws_file = r"C:\test\hru\7\or_ws_7" # INPUT Raster
    ab_file = r"C:\test\hru\7\or_ab_7"   # INPUT Raster
    elev_file = r"C:\test\hru\7\or_elev"  # INPUT Raster
    lc_file = r"C:\test\hru\7\or_lc_2k_rec" # INPUT Raster
    rad_file = r"C:\test\hru\7\or_rad_4" # INPUT Raster 
    workSpace = r"C:\test\hru\7"       # OUTPUT Directory
    #maskLayer = r"C:\test\test\5\or_ws_bnd2_buf1km.shp"
    HRUName = "or_2000_74" # Input HRU
    #
    # Monitor Time Elapsed
    # ===================================
    beginTime = time.clock()
    print ("\nChecking files and directories")

    # Create output folder
    outWorkSpace = os.path.join ( workSpace + os.sep, output )
    if checkFolderStatus( outWorkSpace ) == False:
        createOutputFolder( outWorkSpace );

    env.workspace = outWorkSpace
    #env.mask = maskLayer
    HRUEXP = Raster(ws_file) * 100000000 + Raster(ab_file) * 100000 + Raster(elev_file) * 1000 + Raster(lc_file) * 10 + Raster(rad_file)
    print HRUEXP.isTemporary
    HRUEXP.save(os.path.join ( outWorkSpace + os.sep, HRUName ))
    HRU = os.path.join ( outWorkSpace + os.sep, HRUName )
    print HRU
    
    # Process: Raster to Polygon
    SHPName = HRUName + shpExt
    SHP = os.path.join ( outWorkSpace + os.sep, SHPName )
    rasterConversion( outWorkSpace, HRU, SHP );
    print SHP
    
    # Process: Dissolve
    SHPDisName = renameStrings( HRUName, "dis", underScore ) + shpExt
    SHPDis = os.path.join ( outWorkSpace + os.sep, SHPDisName )
    print SHPDis
    inputList = [ dissolve_field ]
    dissolveManagement( outWorkSpace, SHP, SHPDis, inputList );
    
    # Process: Add Field + Calculate Field
    addcalculate_FieldManagement( outWorkSpace, SHPDis );

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
