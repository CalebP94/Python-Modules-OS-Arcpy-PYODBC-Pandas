import arcpy, time
from arcpy import env
## Set your environmental variables: workspace, coordinates, overwrite
env.overwriteOutput = True


mh_reh_sum = 'C:\\Personal_Sewer\\Active\\SS6786\\FY17-18\\SS6786(17-18) ANNUAL MANHOLE REHAB_FINAL WORK SUMMARY MAJOR.csv'
CIP = 'SS6786'
CONTRACT = "TEST"
C_SID= 100
ssManholeQC = 'C:\\CheckIn\\CheckOutCP.gdb\\Sewer\\ssManhole'
rehabTable = 'C:\\CheckIn\\CheckOutCP.gdb\\ssManhole_RehabSummary'
outAppend = 'appendTable'
qcTable = 'SS6786_PayApp_1718_QC_Major'
wsp_mh_reh_sum = 'SS6786_PayApp_1718_Major'
db_main = 'C:\Personal_Sewer\Active\SS6786\FY17-18\SS6786_1718.gdb'

def change_fldtype(in_table, in_fld, out_fld_type): ##Change field type
    if out_fld_type == "TEXT":
        arcpy.management.AddField(in_table, "temp", out_fld_type, "", "", 255)
        arcpy.management.CalculateField(in_table, "temp", "[{}]".format(in_fld))
        arcpy.management.DeleteField(in_table, in_fld)
        arcpy.management.AddField(in_table, in_fld, out_fld_type, "", "", 255)
        arcpy.management.CalculateField(in_table, in_fld, "[temp]")
        arcpy.management.DeleteField(in_table, "temp")
    else:
        arcpy.management.AddField(in_table, "temp", out_fld_type)
        arcpy.management.CalculateField(in_table, "temp", "[{}]".format(in_fld))
        arcpy.management.DeleteField(in_table, in_fld)
        arcpy.management.AddField(in_table, in_fld, out_fld_type)
        arcpy.management.CalculateField(in_table, in_fld, "[temp]")
        arcpy.management.DeleteField(in_table, "temp")
def manholeRehab():
    arcpy.AddMessage("Processing Manhole Rehab Summary...")
#ADD CWS PAY APP TO TEMP MEMORY
    mh_reh_sum_mem = arcpy.management.CopyRows(mh_reh_sum, r"in_memory/mh_reh_sum_mem")
#ADD WSP MANHOLE REHAB TO TEMP MEMORY
    append_table_mh = arcpy.CreateTable_management(r"in_memory", r"mhAppender_Rehab", rehabTable)
#ADD WSP MANHOLE NO JOIN TABLE TO TEMP MEMORY
    qc_table_mh = arcpy.CreateTable_management(r"in_memory", r"mhQC_Rehab", rehabTable)
    """
    DEV SCRIPT
    ------------
    ECheck fields in memory table
    ##    fields = [mh.name for mh in arcpy.ListFields(mh_reh_sum_mem)]
    ##    print fields
    """
    arcpy.management.AlterField(mh_reh_sum_mem, 'Install_Internal_24"_Flex_Chimney_Seal', "Internal_Chimney_Seal__24__")
##    arcpy.management.AlterField(mh_reh_sum_mem, 'Install_Internal_36"_Flex_Chimney_Seal', "Internal_Chimney_Seal__36_")
    arcpy.management.AlterField(mh_reh_sum_mem, 'Install_External_24"_Flex_Chimney_Seal', "External_Chimney_Seal__24_")
    arcpy.management.AlterField(mh_reh_sum_mem, 'Date_of_Repair__MM_DD_YYYY_', "DATE")
    arcpy.management.AlterField(mh_reh_sum_mem, 'Manhole_Asset_ID', "FACILITYID")
    arcpy.management.AlterField(mh_reh_sum_mem, 'Contractor_Comments', "COMMENTS")
    arcpy.management.AlterField(mh_reh_sum_mem, 'Subbasin__e_g__BR02_', "SUBBASIN")
    arcpy.management.AddField(mh_reh_sum_mem, "REHABCAT", "SHORT")
    arcpy.management.AddField(mh_reh_sum_mem, "REHABTYPE", "SHORT")
    arcpy.management.AddField(mh_reh_sum_mem, "CIPNUM", "TEXT", "", "", 255)
    arcpy.management.AddField(mh_reh_sum_mem, "CONTRACTORSID", "SHORT")
    arcpy.management.AddField(mh_reh_sum_mem, "CONTRACTOR", "TEXT")
    arcpy.management.AddField(mh_reh_sum_mem, "VERTFT", "DOUBLE")
    arcpy.management.AddField(mh_reh_sum_mem, "SUBBASIN", "STRING")
    arcpy.management.AddField(mh_reh_sum_mem, "WSP_ID", "LONG")
    """
    Check fields in memory table
    DEV SCRIPT
    ------------
    ##    fields = [mh.name for mh in arcpy.ListFields(mh_reh_sum_mem)]
    ##    print fields
    """
#Ensure fields are of proper data type
    if [x.type for x in arcpy.ListFields(mh_reh_sum_mem) if x.name == "DATE"][0] != "Date":
        change_fldtype(mh_reh_sum_mem, "DATE", "DATE")
    if [x.type for x in arcpy.ListFields(mh_reh_sum_mem) if x.name == "FACILITYID"][0] != "String":
        change_fldtype(mh_reh_sum_mem, "FACILITYID", "TEXT")
    if [x.type for x in arcpy.ListFields(mh_reh_sum_mem) if x.name == "COMMENTS"][0] != "String":
        change_fldtype(mh_reh_sum_mem, "COMMENTS", "TEXT")
##    if [x.type for x in arcpy.ListFields(mh_reh_sum_mem) if x.name == "Riser_Diameter__inches_"][0] != "Double":
##        change_fldtype(mh_reh_sum_mem, "Riser_Diameter__inches_", "DOUBLE")
#Cursor to access contractor work summary table records, define fields...
    cursor = arcpy.da.UpdateCursor(mh_reh_sum_mem, ["Manhole_Lined__CA_AL__X_if_applicable_",#0
                                                    "Manhole_Lined__CA_AL__X_if_applicable_1",#1
                                                    "Remove_and_Reset_Existing_Frame_and_Cover__X_if_applicable_",#2
                                                    "Replace_Standard_Frame_Cover__X_if_applicable_",#3
                                                    "Replace_Watertight_Frame_Cover__X_if_applicable_",#4
                                                    'Internal_Chimney_Seal__24__',#5
                                                    'Inverts',#6
                                                    'Inverts_1',#7
                                                    'Remove_and_Replace_Internal_Drop_Connection__X_if_applicable_',#8
                                                    'External_Chimney_Seal__24_',#9

                                                    "DATE","FACILITYID", "REHABCAT",#(-10,-9,-8)
                                                    "REHABTYPE", "COMMENTS", "CIPNUM",#(-7,-6,-5)
                                                    "CONTRACTOR", "SUBBASIN", "WSP_ID","CONTRACTORSID"])#(-4,-3,-3,-1)

#Create cursor for inserting contractory work summary tables into temporary WSP rehab table and qc table
    fields = [mh.name for mh in arcpy.ListFields(mh_reh_sum_mem)]
    print(fields)
    """
    #TEMP WSP Table
    """
    appendFields = [u'DATE', u'FACILITYID', u'REHABCAT', u'REHABTYPE', u'COMMENTS', u'CIPNUM', u'CONTRACTOR', u'SUBBASIN', u'WSP_ID', u'CONTRACTORSID']
    updateCursor = arcpy.da.UpdateCursor(append_table_mh, appendFields)
    appendCursor = arcpy.da.InsertCursor(append_table_mh, appendFields)
    """
    #TEMP QC Table
    """
    qcCursor = arcpy.da.InsertCursor(qc_table_mh, appendFields)
    readQcCursor = arcpy.da.UpdateCursor(qc_table_mh, appendFields)
    """
    #Manhole Feature - Access Facilityids
    """
    readMHcursor = arcpy.da.SearchCursor(ssManholeQC, "FACILITYID")
#Read temporary table records... acessing most recent WSP ID
##    try:
    totalCounter = 0
    errorCounter = 0
    passCounter = 0
    wspLatestID = 0
    for row in cursor:
        if row[0] is not None or row[1] is not None:
            totalCounter+=1
            passCounter+=1
            row[-8] = 1
            row[-7] = 2
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
        if row[2] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 2
            row[-7] = 2
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
#fields calculated
##["Pay_App_No_","Manhole_Completely_Replaced___Install_New_Manhole__X_if_applicable_", "Manhole_Lined__CA_AL__X_if_applicable_",
        if row[3] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 2
            row[-7] = 1
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
        if row[4] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 2
            row[-7] = 4
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
        if row[5] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 3
            row[-7] = 1
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
#fields calculated
##"Replace_Standard_Frame_Cover__X_if_applicable_", "Remove_and_Reset_Existing_Frame_and_Cover__X_if_applicable_","Replace_Watertight_Frame_Cover__X_if_applicable_",
            appendCursor.insertRow(row[-10:])
        if row[6] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 5
            row[-7] = 1
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
        if row[7] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 4
            row[-7] = 1
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
#fields calculated
## "Internal_Chimney_Seal__24__", "Internal_Chimney_Seal__36_",
            appendCursor.insertRow(row[-10:])
        if row[8] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 7
            row[-7] = 1
            cursor.updateRow(row)
        if row[9] is not None:
            #print row[1:-11]
            totalCounter+=1
            passCounter+=1
            row[-8] = 3
            row[-7] = 1
            cursor.updateRow(row)
            appendCursor.insertRow(row[-10:])
        if(row[0] is None and row[1] is None and row[2] is None
           and row[3] is None and row[4] is None
           and row[5] is None and row[6] is None
           and row[7] is None and row[8] is None
           and row[9] is None):
            print row[-10:]
            qcCursor.insertRow(row[-10:])
    arcpy.management.AddField(append_table_mh, "JOINED", "TEXT")
    arcpy.management.AddField(qc_table_mh, "JOINED", "TEXT")
    cursorII = arcpy.da.UpdateCursor(append_table_mh, ["FACILITYID", "JOINED"])
    fcd = {}
    for row in readMHcursor:
        fcd[row[0]]='JOINED'
    for row in cursorII:
        mhID = row[0]
        if mhID in fcd:
            row[1] = fcd[mhID]
            cursorII.updateRow(row)

    arcpy.conversion.TableToTable(append_table_mh, db_main, wsp_mh_reh_sum)
    arcpy.conversion.TableToTable(qc_table_mh, db_main, qcTable)

##    except Exception as e:
##        print(e)
    arcpy.management.Delete(r"in_memory")
if mh_reh_sum!='':
    manholeRehab()