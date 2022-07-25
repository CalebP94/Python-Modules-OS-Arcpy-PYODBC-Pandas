
import arcpy
import sys
import os
import csv
import arcpy


def produceXY(nearTable, waMeter, points):

    addressNearTableArr = []
    bothFeaturesObjArr = []
    final = []
    pointXY = []
    oidArr = []

    with arcpy.da.SearchCursor(nearTable, ['IN_FID', 'NEAR_FID']) as nearTableSearcher:
        for row in nearTableSearcher:
                vertices = row[1]
                waterID = row[0]
                bothObj =(waterID, vertices)
                bothFeaturesObjArr.append(bothObj)

    print(bothFeaturesObjArr)
    with arcpy.da.SearchCursor(points, ['ObjectID', 'SHAPE@X', 'SHAPE@Y']) as sCursor:
        for row in sCursor:
            objID = row[0]
            pointX = row[1]
            pointY = row[2]
            for row in bothFeaturesObjArr:
                waterObjsId = row[0]
                #print(addressObjID, row[0])
                if objID == row[1]:
                    #print('ADDRESS XY', addressObjID, pointX, pointY)
                    returner = ('Densified Vertex', objID, pointX, pointY, 'Water XY', waterObjsId)
                    pointXY.append(returner)
                else:
                    continue

    with arcpy.da.SearchCursor(waMeter, ['ObjectID', 'FacilityID', 'SHAPE@X', 'SHAPE@Y', 'MeterNumber']) as sCursorWaterMeter:
        for row in sCursorWaterMeter:
            waMeterObjId = row[0]
            facilityId = row[1]
            pointX = row[2]
            pointY = row[3]
            meterID = row[4]
            for row in pointXY:
                labelAdd = row[0]
                vertexObj = row[1]
                pointXAdd = row[2]
                pointYAdd = row[3]
                labelWater = row[4]
                obj = row[5]
                if(waMeterObjId == row[5]):
                    returner = (labelAdd, vertexObj, pointXAdd, pointYAdd, labelWater, obj,meterID, facilityId, pointX, pointY)
                    final.append(returner)
                else:
                    continue
        print('XY Production Complete')
        print(final)
        return final
##        if len(final) > 0:
##            return final
##        else:
##            return None

#---------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------

def csvProduction(inData, pathAndCSVname):
    print("Starting CSV Production")
    with open(pathAndCSVname, 'wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['PointLabel', 'PointObjectId', 'PointXpoint', 'PointYpoint', 'WaterLabel', 'WaterObjectId', 'MeterID', 'FacilityID', 'WaterPointX', 'WaterPointY'])
        for row in inData:
            csv_out.writerow(row)

#---------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------

def outPutAll(grid):
    fields = ['OID']
    field = 'OID'
    oidArr = []
    nearTable = 'C:\\Personal_Sewer\\Active\\AMI\\AMI_Working.gdb\\waMeter_waMainPoints_NearTable_Grid'
    waMeter = 'C:\\Personal_Sewer\\Active\\AMI\\AMI_Working.gdb\\waMeter_SystemWide_NoServiceLineIntersect'
    valve = 'C:\\Personal_Sewer\\Active\\AMI\\AMI_Working.gdb\\densified\\waWaterMain_Grid'
    csv = 'C:\Personal_Sewer\Active\AMI\ServiceLineProduction_CSV'
    outFeature = 'C:\Personal_Sewer\Active\AMI\AMI_Working.gdb\waServiceLine\waServiceLine_Grid'
    with arcpy.da.SearchCursor(grid, fields) as sCursor:
        for row in sCursor:
            #nearTableFormat = nearTable + '{}'.format(arcpy.AddFieldDelimiters(grid, field), row[0])

            print('Processing Grid {}'.format(row[0]))

            nearTableFormat = nearTable + '{}'.format(row[0])
            valveFormat = valve + '{}'.format(row[0])
            values = produceXY(nearTableFormat, waMeter, valveFormat)

            print('VALUES', values)
            csvOutPuter = csv + '{}.csv'.format(row[0])
            csvProduction(values,csvOutPuter)
##            if values is not None:
##                csvOutPuter = csv + '{}.csv'.format(row[0])
##                csvProduction(values,csvOutPuter)
##
##                print('CSV', csvOutPuter)
##
##                outFeatureGrid = outFeature + '{}'.format(row[0])
##                arcpy.management.XYToLine(csvOutPuter, outFeatureGrid, 'PointXpoint', 'PointYpoint', 'WaterPointX', 'WaterPointY', 'MeterID')

outPutAll('C:\Personal_Sewer\Active\AMI\AMI_Working.gdb\waGrid')



