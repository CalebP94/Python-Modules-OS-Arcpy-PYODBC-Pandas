
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Import necessary modules for application
"""
from arcpy import env

import pandas as pd

import os

import numpy

##import Tkinter
##from Tkinter import *
###from tikinter import ttk

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Step #1
Return Gravity Main IDs for Join with Contractor Work Summary
"""
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def featureIDs(feature, featureAttr):
    featureIDs = []
    returnArr = []
    with arcpy.da.SearchCursor(feature, featureAttr) as sCursor:
        print("Accessing feature data")
        for row in sCursor:
            appender = [row[0], 'Join']
            featureIDs.append(appender)

    df = pd.DataFrame(featureIDs, columns=[featureAttr, "Join_Indicator"])
    return df

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Step #2
QC-1 & Join
"""
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def readCWS_QC1(path, column):
    df = pd.read_excel(open(path, 'rb'))

    #QC-1-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Replace wrong character that divies the us from ds in gravity main
    """
    facilityIDQC = df[column].str.replace('-', '_')
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    Join to ssGravityMain Ids from featureIDs function
    """
    df[column] = facilityIDQC
    print(df[column])
    updatedDF = df.set_index(column).join(cityFeatureId.set_index(field))

    return updatedDF

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Step #3
Reformat data frame for better ArcTable production
"""
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def reformatQC1(updatedDF):
    newColumns = ["DATE", "Pay App", "SUBBASIN", "Address", "Mech_Heavy_Sewer_Cleaning", "Pipe_Burst", "CIPP", "Open_Cut", "PTREPAIRLOC", "PTREPAIRMAT", "PRD_0_8",
                    "PRD_8_16", "PRD_16", "Paved or Unpaved", "DIAMETER", "REHABLENGTH", "Comments", "Join_Indicator"]

    updatedDF.columns = newColumns
    updatedDF.index.name = "FACILITYID"
    updatedDF.columns = [column.replace(" ", "_") for column in updatedDF.columns]


    return updatedDF

###---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
###---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Step #4
QC-2 where Null Joins occur switch upstream downstream
"""
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def nullJoinRevisions(updatedDF):
    noJoins = updatedDF.query("Join_Indicator.isnull()")
    us=noJoins.index.str.split('_').str.get(0)
    ds=noJoins.index.str.split('_').str.get(1)
    ds_us = ds.map(str) + '_' + us.map(str)
    us_ds = us.map(str) + '_' + ds.map(str)
    df_ds_us = pd.DataFrame(ds_us)
    df_ds_us = df_ds_us.assign(US_DS = pd.Series(us_ds, dtype=str))
    df_ds_usJoin = df_ds_us.set_index(0).join(cityFeatureId.set_index(field))
    df_ds_usJoin.index.name = "FacilityId"


    updateNaNs = df_ds_usJoin.query('Join_Indicator == "Join"')
    updateNaNsIndex = updateNaNs.index
    updateNaNs["Correct_FacilityID"] = updateNaNsIndex
    updateNaNs.index = updateNaNs["US_DS"]
    updateNaNs.index.name='FacilityId'
    updateNaNs.drop('US_DS', axis=1,inplace=True)
    updatedDF = updatedDF.join(updateNaNs, lsuffix="_FacilityId_Original", rsuffix="_FacilityId_Corrected")
    updatedDFAppend= updatedDF.query("Join_Indicator_FacilityId_Corrected == 'Join'")
    updatedDFAppend.index = updatedDFAppend['Correct_FacilityID']
    #updatedDF_Deleter = updatedDF.query("Join_Indicator_FacilityId_Corrected == 'Join'").index
    finalDF = updatedDF.append(updatedDFAppend)
##    finalDF.index.name="FacilityId"
##    for ind in updatedDF_Deleter:
##        print(ind)
##        finalDF.drop(labels=ind, axis=0)
    #finalDF.to_csv(export)
    return finalDF

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Step #5
Remove errant IDs that have been corrected in QC-2 so ArcTable does not have them
"""
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def removeOriginalError(updatedDF):
    updatedDF_Deleter = updatedDF.query("Join_Indicator_FacilityId_Corrected == 'Join'").index
    for ind in updatedDF_Deleter:
        print(ind)
        updatedDF.drop(labels=ind, axis=0)
    return updatedDF

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Step #6
Produce CSV
"""
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def csvProduction(finalDF, export):
    finalDF.index.name="FACILITYID"
    try:
        finalDF.to_csv(export)
        os.startfile(export)
    except UnicodeEncodeError:
        pass

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Call Step #1

ENTER THE SOURCE FEATURE YOU FIND IN YOUR VERSIONED DATA IN THE GUI
"""
field = "FacilityID"
print("ENTER THE SOURCE FEATURE")
source = raw_input("File Path to source feature to be used for QCing Pay App: ")
#setting up user input:
#source='C:\\CheckIn\\20220207\\CheckOutCP.gdb\\Sewer\\ssGravityMain'
##source = simpledialog.askstring(title="Step #1",
##                                 promt = "Enter the path to the source feature involved in QC: ")

cityFeatureId = featureIDs(source, field)

###---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Call Step #2
QC-1 and Join
"""
"""Path to CWS"""
##xlsx = easygui.enterbox("Contractor Pay Application Source (excel document): ")
#xlsx = 'R:\Projects\Active\CW2020_Master\Working\Cityworks\Cityworks_WorkSummary_Integration\Gravity Mains\SS6966 Rehab\FY21-22\Pay App\SS6966 (20-21) CWS - Payapp 8 and 9 - RAW.xlsx'
print("Enter file path and file name where you are storing the Pay Application input")
xlsx = raw_input('File Path to Payp being QCed (include file name e.g. SS6966.xlsx): ')
"""Field Name in CWS"""
key = 'Main Line Asset ID'
"""Implement previous variables in function"""
#readCWS_QC1(xlsx,key)
df_Step2 = readCWS_QC1(xlsx, key)
###---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
###---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Call Step #3 reformat qc1
"""
df_Step2_Reformat = reformatQC1(df_Step2)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
""" Step 4"""
updatedDF = nullJoinRevisions(df_Step2_Reformat)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""Step 5"""
finalDF = removeOriginalError(updatedDF)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""Step 6"""
#outPut = "R:\\Projects\\Active\CW2020_Master\\Working\\Cityworks\\Cityworks_WorkSummary_Integration\\Gravity Mains\\SS6966 Rehab\\FY21-22\Pay App\\TableProduction\\SS6966_PayApp_8_thru_9_AUTO.csv"
outPut = raw_input("Your Generated CSV Output: ")
csvProduction(finalDF, outPut)