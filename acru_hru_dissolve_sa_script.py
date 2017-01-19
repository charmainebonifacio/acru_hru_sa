############################################################################################
# TITLE        : HRU_DISSOLVE
# CREATED BY   : Charmaine Bonifacio
# DATE CREATED : July 2, 2014
# EDITED BY    : Charmaine Bonifacio
# DATE EDITED  : July 3, 2014
#------------------------------------------------------------------------------------------
# DESCRIPTION  : This python script checks the field names and dissolves the shapefiles
#                accordingly.
#------------------------------------------------------------------------------------------
# INPUT        : <> Workspace
# OUTPUT       : <> Create an output folder that contains the following:
#                   <> Disolved Shapefiles
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

# File Variables
global fileType
global dbfExt
global shpExt
dbfExt = '.dbf'
shpExt = '.shp'

# Miscellaneous variables:
global underScore
global output
underScore = "_"
output = "Results"

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
# FUNCTION: dissolveManagement
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

############################################################################################
# MAIN FUNCTION
#-------------------------------------------------------------------------------------------
def main():
    # Obtain Input From User
    workSpace = r"C:\test\hru\7\Final_Sub\PreProcessed"       # OUTPUT Directory
    #
    # Monitor Time Elapsed
    # ===================================
    beginTime = time.clock()
    print ("\nChecking files and directories")

    # Create output folder
    outWorkSpace = os.path.join ( workSpace + os.sep, output )
    if checkFolderStatus( outWorkSpace ) == False:
        createOutputFolder( outWorkSpace );

    # Check Field Names
    env.workspace = workSpace
    featureList = arcpy.ListFeatureClasses()
    for fc in featureList:
        env.workspace = workSpace
        fieldCount = 0
        dissolve_field = "x_id"
        fields = arcpy.ListFields(fc)
        for field in fields:
            fieldCount += 1
            if fieldCount == 6:
                dissolve_field = field.name
        # Process: Dissolve
        outFileName = "Dissolved_" + fc
        outFile = os.path.join ( outWorkSpace + os.sep, outFileName )
        inFile = os.path.join ( workSpace + os.sep, fc )
        tempLayer = "input"
        
        print("\nProcessing file: {0}".format(fc))        
        print("Fields found: {0}".format(fieldCount))
        print("Field to dissolve: {0}".format(dissolve_field))
        print("Dissolved shapefile found here: {0}".format(outFile))
        inputList = [ dissolve_field ]
        arcpy.MakeFeatureLayer_management(fc,tempLayer)
        dissolveManagement( outWorkSpace, tempLayer, outFileName, inputList );
    
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
