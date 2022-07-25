import pyodbc
import os, sys
import csv

pathMBD_P= 'C:\\Personal_Sewer\\Active\\REHAB_SUBMITTALS_MBD\\P'
pathMBD_M= 'C:\\Personal_Sewer\\Active\\REHAB_SUBMITTALS_MBD\\M'
pathMBD_Other = 'C:\\Personal_Sewer\\Active\\REHAB_SUBMITTALS_MBD\\Other'


def mineCippPipes(source):
    dbArr = []
    cipp_pipes=[]
    for path, subdirs, files in os.walk(pathMBD_P, topdown=True):
        for row in files:
            append = path + '\\' + row
            dbArr.append(append)
    

    tableNumber = len(dbArr)
    inspectionsCount = 0
    for row in dbArr:
        dbq = 'DBQ={};'.format(row)
    
        drive = r'DRIVER={Microsoft Access Driver (*.mdb)};'
        conn_str = (drive + dbq)
        try:
            cnxn = pyodbc.connect(conn_str)
            cursor = cnxn.cursor()
            cursor.execute("select Pipe_Segment_Reference, Lining_Method, Drainage_Area, Date from Inspections")
            try:
                for row in cursor.fetchall():
                    cipp_pipes.append(row)
            except Exception as e:
                print(e)
            for row in cursor.tables():
                if row.table_name == 'Inspections':
                    inspectionsCount+= 1
                    print(row.table_name, inspectionsCount, tableNumber)
                    #cursor.execution('SELECT * FROM Inspections')
                    

        except Exception as e:
            print("FAIL", conn_str, e)   
    print(cipp_pipes)
    return cipp_pipes

def writeCSV(arr, path, method):
    with open(path, method) as file:
        mywriter = csv.writer(file, delimiter=',')
        mywriter.writerows(arr)


cipp = mineCippPipes(pathMBD_P)
writeCSV(cipp, 'C:\Personal_Sewer\Active\REHAB_SUBMITTALS_MBD\PACP_CIPP.csv', 'wb')