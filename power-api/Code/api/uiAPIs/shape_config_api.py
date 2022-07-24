from flask import request, jsonify, Blueprint, Response, current_app
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile
import json
from datetime import datetime, date
import re
import io
import requests
import random 
import os.path


FILE_DIRECTORY = '/api/uiAPIs/'
shapeConfigApi = Blueprint('shapeConfigApi', __name__)

CONNECT = os.environ.get('eka_connect_host')
#CONNECT = 'http://192.168.1.225:7073'

df_combined = pd.DataFrame(np.zeros((0,0)))

@shapeConfigApi.route('/shape/file', methods=['POST'])
def get_file():
    req_data = request.get_json()
    req_headers = dict(request.headers)
    if req_data['dropdown'] == 'All':
        Quantity_fileName = checkAndDownloadFile(req_data['fileDetails']['Quantity'], req_headers)
        Price_fileName =  checkAndDownloadFile(req_data['fileDetails']['Price'], req_headers)
        Quantity_filePath = FILE_DIRECTORY + Quantity_fileName
        df_quality = pd.read_csv(Quantity_filePath, encoding = "ISO-8859-1", parse_dates=['Date'])
        
        Price_filePath = FILE_DIRECTORY + Price_fileName
        df_price = pd.read_csv(Price_filePath, encoding = "ISO-8859-1", parse_dates=['Date'])
        cols = list(df_quality.columns)
        cols.pop(0)
        global df_combined
        df_combined['Date'] = df_quality['Date'].dt.strftime("%d-%m-%Y")
        for col in cols:
            df_combined[col] = df_quality[col].map(str) + '  |  ' + df_price[col].map(str)    
        return jsonify({'msg': 'file combined successfully'})
    else :
        dropdown = req_data['dropdown']
        fileName = checkAndDownloadFile(req_data['fileDetails'][dropdown], req_headers)
        filePath = FILE_DIRECTORY + fileName
        df = pd.read_csv(filePath)
        current_app.logger.info(fileName)
        return jsonify({'msg': 'file fetched successfully'})

def checkAndDownloadFile(fileDetails, req_headers):
    filePath = FILE_DIRECTORY + fileDetails['fileName']
    if os.path.exists(filePath):
        return fileDetails['fileName']
    if fileDetails['id']:
        headers = getFileAPI_headers(req_headers)
        headers["storageType"] = "awsS3"
        headers["folderInS3"] = "powerDocs"
        body = getFileAPI_body(fileDetails)
        resp = requests.post(CONNECT + '/download', json = body, headers = headers)
        current_app.logger.info(fileDetails['fileName'])
        filePath = FILE_DIRECTORY + fileDetails
        with open(filePath, "w+b") as f:
            f.write(resp.content)
        return fileDetails['fileName']


@shapeConfigApi.route('/shape/columns', methods=['POST'])
def get_columns():
    req_data = request.get_json()
    fileName = req_data['fileName']
    if fileName == 'All':
        cols = list(df_combined.columns)
        response_wrap = jsonify({ "columns" : cols })
        result = response_wrap
        current_app.logger.info(result)
        return result
    else:
        filePath = FILE_DIRECTORY + fileName
        df = pd.read_csv(filePath, encoding = "ISO-8859-1")
        cols = list(df.columns)
        response_wrap = jsonify({ "columns" : cols })
        result = response_wrap
        current_app.logger.info(result)
        return result 

@shapeConfigApi.route('/shape/data', methods=['POST'])
def get_rows():
    req_data = request.get_json()
    startingRow = int(req_data['startingRow'])
    endingRow = startingRow + 100
    fileName = req_data['fileName']
    startDate = req_data['startDate'].split()
    endDate = req_data['endDate']
    if fileName == 'All':
        current_app.logger.info(df_combined.head(5))
        rows = df_combined.iloc[startingRow : endingRow]
        data_rows = rows.to_json(orient='records')
        response_wrap = jsonify({ "rows" : data_rows })
        current_app.logger.info(response_wrap)
        return response_wrap
    else:
        mydateparser = lambda x: pd.to_datetime(x, dayfirst=True)
        filePath = FILE_DIRECTORY + fileName
        df = pd.read_csv(filePath, encoding = "ISO-8859-1", parse_dates=['Date'], date_parser=mydateparser)
        df['Date'] = df['Date'].dt.strftime("%d-%m-%Y")
        rows = df.iloc[startingRow : endingRow]
        data_rows = rows.to_json(orient='records')
        response_wrap = jsonify({ "rows" : data_rows })
        current_app.logger.info(response_wrap)
        return response_wrap

@shapeConfigApi.route('/shape/update', methods=['POST'])
def update_value():
    req_data = request.get_json()
    rowIndex = int(req_data['rowIndex'])
    colIndex = int(req_data['colIndex'])

    if req_data['attribute'] == 'All':
        Quantity = req_data['Quantity']
        Price = req_data['Price']

        Quantity_file = req_data['Quantity_file']
        Quantity_filePath = FILE_DIRECTORY + Quantity_file
        df1 = pd.read_csv(Quantity_filePath, encoding = "ISO-8859-1")
        df1.iloc[rowIndex,colIndex] = req_data['Quantity']  
        df1.to_csv(Quantity_filePath, index=False, date_format="%d-%m-%Y")

        Price_file = req_data['Price_file']
        Price_filePath = FILE_DIRECTORY + Price_file
        df2 = pd.read_csv(Price_filePath, encoding = "ISO-8859-1")
        df2.iloc[rowIndex,colIndex] = req_data['Price'] 
        df2.to_csv(Price_filePath, index=False, date_format="%d-%m-%Y")

        msg = 'row {} col {} , File {} with Quanity {} and File {} with Price {}'.format(rowIndex,colIndex,Quantity_file,Quantity,Price_file,Price)
        return jsonify({'msg': msg})
    else :
        value = req_data['value']
        fileName = req_data['fileName']
        filePath = FILE_DIRECTORY + fileName
        df = pd.read_csv(filePath, encoding = "ISO-8859-1")
        df.iloc[rowIndex,colIndex] = value
        df.to_csv(filePath, index=False, date_format="%d-%m-%Y")
  
        msg = 'row {} col {} of File {} update with {}'.format(rowIndex,colIndex,fileName,value)
        return jsonify({'msg': msg})

def getFileAPI_headers(req_headers):
    headers = {
        "Authorization": req_headers['Authorization'],
        "Content-Type": "application/json",
        "X-TenantID": req_headers['X-Tenantid'],
        "storageType":"fileSys"
    }
    return headers

def getFileAPI_body(req_body):
    body = {
        "id": req_body['id'],
        "refObjectId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
        "fileContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "fileName": req_body['fileName']
    }
    return body

@shapeConfigApi.route('/filedownload', methods=['POST'])
def file_download():
    req_data = request.get_json()
    req_headers = dict(request.headers)
    req_body = dict(req_data)

    new_fileName = req_body['id'] + ".csv"

    headers = getFileAPI_headers(req_headers)
    body = getFileAPI_body(req_body)

    resp = requests.post(CONNECT + '/download', json = body, headers = headers)
    current_app.logger.info(new_fileName)
    filePath = FILE_DIRECTORY + new_fileName
    with open(filePath, "w+b") as f:
        f.write(resp.content)
    
    startDate = reverseDate(req_body["startDate"])
    endDate = reverseDate(req_body["endDate"])
    mydateparser = lambda x: pd.to_datetime(x, dayfirst=True)
    filePath = FILE_DIRECTORY + new_fileName
    df = pd.read_csv(filePath, encoding = "ISO-8859-1", parse_dates=['Date'], date_parser=mydateparser, index_col="Date")
    displayRange = df[startDate:endDate]
    displayRange.to_csv(filePath, date_format="%d-%m-%Y")

    validity = {}
    if req_data['timeFrequency']:
        validity = testValidateColumnFreq(new_fileName, req_data['timeFrequency'])
    else:
        validity = {'validity': False, 'msg' : 'timeFrequency not present in payload'}

    return jsonify({'fileName': new_fileName, 'timeFrequencyValidity': validity})

    # rng = pd.date_range(start=startDate, end=endDate, freq="D")
    # rng.size

    # excel_dates = displayRange.index.to_series()
    # excel_dates.reset_index(inplace=True, drop=True) 

    # generated_dates = rng.to_series()
    # generated_dates.reset_index(inplace=True, drop=True)

    # comparision_array = displayRange.index == rng
    # all_dates_available = np.all(comparision_array)

    # comparision_series = pd.Series(comparision_array)
    # comparision_df = pd.concat([excel_dates,generated_dates,comparision_series], axis=1)
    # comparision_df.columns = ["excel_dates","required_dates","comparision_series"]
    # _resp = comparision_df.iloc[:]
    # resp = _resp.to_json(orient='records')
    # response_wrap = { "rows" : resp }

    # return {"all_dates_available": str(all_dates_available), "matrix" :response_wrap, 'fileName': new_fileName}

def reverseDate(date):
    _temp = date.split("-")
    _temp.reverse()
    result = '-'.join([str(elem) for elem in _temp]) 
    return result

@shapeConfigApi.route('/shape/validate', methods=['POST'])
def validate():
    req_data = request.get_json()
    startDate = req_data['startDate']
    endDate = req_data['endDate']
    rng = pd.date_range(start=getRngDate(startDate), end=getRngDate(endDate), freq="D")
    rngSize = rng.size
    result = { }
    if req_data["priceFile"]:
        fileName = req_data["priceFile"]
        mydateparser = lambda x: pd.to_datetime(x, dayfirst=True)
        filePath = FILE_DIRECTORY + fileName
        df = pd.read_csv(filePath, encoding = "ISO-8859-1", parse_dates=["Date"],date_parser=mydateparser, index_col="Date")
        price_rng = df[startDate:endDate].index
        price_rngSize = price_rng.size
        if rngSize != price_rngSize:
            result['price'] = 'price range not matching in data'
        elif rng == price_rng:
            result['price'] = 'price ranges are matching'

def getRngDate(date):
    temp = date.split("-")
    temp.reverse()
    result = '-'.join([str(elem) for elem in temp]) 
    return result

@shapeConfigApi.route('/shape/fileUpload', methods=['POST'])
def shape_fileUpload():
    req_headers = dict(request.headers)
    req_data = request.get_json()

    response_obj = {}
    
    fileMeta = {
        "Authorization": req_headers['Authorization'],
        "X-Tenantid": req_headers['X-Tenantid']
    }
    
    for tabName in dict.keys(req_data):
        response_obj[tabName] = {}
        for attribute in dict.keys(req_data[tabName]):
            attribute_data = req_data[tabName][attribute]
            fileMeta['fileName'] = attribute_data["fileName"]
            fileMeta['description'] = "Shape file - "+ tabName +" - "+ attribute
            if 'id' in attribute_data.keys():
                fileMeta['fileId'] = attribute_data['id']
                response_obj[tabName][attribute] = updateFile(fileMeta)
                current_app.logger.info("======== updated file =======")
                current_app.logger.info(response_obj)
            else:
                response_obj[tabName][attribute] = uploadFile(fileMeta)
                current_app.logger.info("********* uploaded new file ********")
                current_app.logger.info(response_obj)
    return jsonify(response_obj)

@shapeConfigApi.route('/shape/copyFile', methods=['POST'])
def copyFile():
    req_data = request.get_json()
    fileName = req_data['copy_from']['fileName']
    filePath = FILE_DIRECTORY + fileName
    df = pd.read_csv(filePath, encoding = "ISO-8859-1")
    new_fileName = fileName + req_data['copy_to']['tab'] + req_data['copy_to']['dropdown'] + '.csv'
    new_filePath = FILE_DIRECTORY + new_fileName
    df.to_csv(new_filePath, index=False, date_format="%d-%m-%Y")
    return jsonify({ 'fileName' : new_fileName, 'tab': req_data['copy_to']['tab'] , 'dropdown': req_data['copy_to']['dropdown'] })


@shapeConfigApi.route('/shape/resetToContracted', methods=['POST'])
def resetToContracted():
    req_data = request.get_json()
    fileName = req_data['fileName']
    filePath = FILE_DIRECTORY + fileName
    df = pd.read_csv(filePath, encoding = "ISO-8859-1")
    if fileName == 'All':
        cols = list(df_combined.columns)
        response_wrap = jsonify({ "columns" : cols })
        result = response_wrap
        current_app.logger.info(result)
        return result
    else:
        filePath = FILE_DIRECTORY + fileName
        df = pd.read_csv(filePath, encoding = "ISO-8859-1")
        cols = list(df.columns)
        response_wrap = jsonify({ "columns" : cols })
        result = response_wrap
        current_app.logger.info(result)
        return result 

@shapeConfigApi.route('/block/blockToExcel', methods=['POST'])
def blockToExcel():
    req_data = request.get_json()
    req_headers = dict(request.headers)
    response_obj = {}
    blockDetails = json.loads(req_data['blockDetails'])
    for block in blockDetails:
        current_app.logger.info(block)
        startDate = getRngDate(block['startDate'])
        endDate = getRngDate(block['endDate'])
        fileName = 'block_' + str(block['blockNo']) + '_' + str(random.randint(1, 10000000)) + '_.csv'
        weekDays = block['weekDays']
        freqWeekDayMapper = {
            "Monday": "W-MON",
            "Friday": "W-FRI",
            "Sunday": "W-SUN",
            "Wednesday": "W-WED",
            "Thrusday": "W-THU",
            "Tuesday": "W-TUE",
            "Saturday": "W-SAT"
        }
        true = True
        false = False
        weekDays = {
            "Monday": true,
            "Friday": true,
            "Holiday": false,
            "Sunday": false,
            "Wednesday": true,
            "Thrusday": true,
            "Tuesday": true,
            "Saturday": false
            }  
        freqNeeded = []
        for day in weekDays:
            if(weekDays[day]):
                    freqNeeded.append(freqWeekDayMapper[day])
        current_app.logger.info(freqNeeded)
        
        dateRange = pd.DatetimeIndex([])
        current_app.logger.info(dateRange)
        for freqDay in freqNeeded:
            current_app.logger.info(freqDay)
            dayRange = pd.date_range(startDate, endDate, freq=freqDay)
            dateRange = dateRange.append(dayRange)
        dateRange = dateRange.sort_values()
        current_app.logger.info(dateRange)

        cols = ["00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00","08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"]
        startIndex = cols.index(block['startTime'])
        endIndex = cols.index(block['endTime'])
        blockCols = cols[startIndex : endIndex]
        
        blockNo = str(block['blockNo'])
        response_obj[blockNo] =  {}

        if block['priceType'] == 'Fixed':
            attributes = ['quantity','price']
            for attribute in attributes:
                df = pd.DataFrame(block[attribute],columns=blockCols, index=dateRange)
                response_obj[blockNo][attribute] = createFile(df, block, fileName, req_headers, attribute)
        else:
            df = pd.DataFrame(block['quantity'],columns=blockCols, index=dateRange)
            response_obj[blockNo]['quantity'] = createFile(df, block, fileName, req_headers, 'quantity')

    current_app.logger.info("the result is")
    response = jsonify(response_obj)
    current_app.logger.info(response)
    return response

def createFile(df, block, fileName, req_headers, attribute):
    response_obj = {}
    df.index.name = 'Date'
    filePath = FILE_DIRECTORY + fileName
    df.to_csv(filePath, date_format="%d-%m-%Y")
    fileMeta = {
        'Authorization' : req_headers['Authorization'],
        'X-Tenantid' : req_headers['X-Tenantid'],
        'fileName' : fileName,
        'description' : 'Block file'
    }
    file_response = {}
    if 'fileDetails' in block.keys():
        fileMeta['fileId'] = block['fileDetails'][attribute]['id']
        file_response = updateFile(fileMeta)
    else:
        file_response = uploadFile(fileMeta)
    return file_response

def uploadFile(fileMeta):
    req_data = request.get_json()
    req_headers = dict(request.headers)
    filepath = FILE_DIRECTORY + fileMeta['fileName']
    headers = {
        "Authorization": fileMeta['Authorization'],
        "X-TenantID": fileMeta['X-Tenantid'],
        "storageType":"awsS3",
        "folderInS3" : "powerDocs"
    }
    files = {
        "file": (fileMeta['fileName'], open(filepath, 'rb'), 'text/plain'),
        "description": (None, fileMeta['description']),
        "refObjectId": (None, "9c86d836-36e7-41f1-bb6f-71efd7df43aa"),
        "refObject": (None, "power"),
    }
    resp = requests.post(CONNECT + '/upload',files=files,headers=headers)
    upload_response = json.loads(resp.text)
    return upload_response

def updateFile(fileMeta):
    req_data = request.get_json()
    req_headers = dict(request.headers)
    filepath = FILE_DIRECTORY + fileMeta['fileName']
    headers = {
        "Authorization": fileMeta['Authorization'],
        "X-TenantID": fileMeta['X-Tenantid'],
        "storageType":"awsS3",
        "folderInS3" : "powerDocs"
    }
    files = {
        "file": (fileMeta['fileName'], open(filepath, 'rb'), 'text/plain'),
        "description": (None, fileMeta['description']),
        "refObjectId": (None, "9c86d836-36e7-41f1-bb6f-71efd7df43aa"),
        "refObject": (None, "power"),
        "fileId" : (None, fileMeta['fileId'])
    }
    resp = requests.post(CONNECT + '/update',files=files,headers=headers)
    update_response = json.loads(resp.text)
    return update_response

def getTimeFrequencyList(freq):
    initialMin = 0
    finalMin = 55
    initialHour = 0
    finalHour = 23
    timeList = []
    hourStr = ""
    while initialHour <= finalHour:
        if initialHour < 10:
            hourStr = '0'+str(initialHour)
        else:
            hourStr = str(initialHour)
        while initialMin <= finalMin :
            if initialMin < 10:
                time = hourStr + ':' + '0' + str(initialMin)
            else:
                time = hourStr + ':' + str(initialMin)
            timeList.append(time)
            initialMin = initialMin + int(freq)
        initialMin = 0
        initialHour = initialHour + 1
    current_app.logger.info('frequency time list :')
    current_app.logger.info(timeList)
    return timeList

def validateColumnFrequency(freq, columns):
    timeList = getTimeFrequencyList(freq)
    current_app.logger.info('The excel column values are:')
    current_app.logger.info(columns.values)
    current_app.logger.info('The validity is as follows:')
    if len(columns.values) == len(timeList):
        validity = (columns.values == timeList)
        if False in validity:
            return {'validity': False, 'msg' : 'Columns names mismatch'}
        else:
            return {'validity': True, 'msg' : 'Number of Columns and Column Names are valid'}
    else:
        return {'validity': False, 'msg' : 'Number of columns mismatch'}

def testValidateColumnFreq(fileName, freq):
    mydateparser = lambda x: pd.to_datetime(x, dayfirst=True)
    filePath = FILE_DIRECTORY + fileName
    df = pd.read_csv(filePath, encoding = "ISO-8859-1", parse_dates=['Date'], date_parser=mydateparser)
    df.pop('Date')
    result = validateColumnFrequency(freq, df.columns)
    current_app.logger.info(result)
    return result

@shapeConfigApi.route('/testJsonDumps', methods=['POST'])
def testJsonDumps():
    current_app.logger.info('json dumps')
    test = json.dumps({'working': 'testing with Response and headers app/json'})
    r = Response(response=test, status=200, mimetype='application/json')
    r.headers["Content-Type"] = "application/json"
    return r

@shapeConfigApi.route('/testDict', methods=['POST'])
def testDict():
    test2 = {'working': 'API is working as dict'}
    return jsonify(test2)

@shapeConfigApi.route('/testString', methods=['POST'])
def testString():
    test3 = 'working as a string'
    current_app.logger.info(test3)
    current_app.logger.info(type(test3))
    return test3

@shapeConfigApi.route('/shape/createInitialShapeFile', methods=['POST'])
def createInitailShapeFile():
    shapeDetails = request.get_json()
    current_app.logger.info(shapeDetails)
    startDate = getRngDate(shapeDetails['startDate'])
    endDate = getRngDate(shapeDetails['endDate'])
    timeFrequency = shapeDetails['timeFrequency']
    generatedFrequency = getTimeFrequencyList(timeFrequency)
    current_app.logger.info(generatedFrequency)

    dateRange = pd.DatetimeIndex([])
    dateRange = pd.date_range(startDate, endDate)
    dateRange = dateRange.sort_values()
    current_app.logger.info(dateRange)

    df = pd.DataFrame(0,columns=generatedFrequency, index=dateRange)
    current_app.logger.info(df)
    fileName = 'shape_' + str(shapeDetails['blockNo']) + '_' + str(random.randint(1, 10000000)) + '.csv'
    filePath = FILE_DIRECTORY + fileName
    #df.to_csv(fileName, index_label='Date', date_format="%d-%m-%Y")
    # Drop to csv w/ context manager          
    df.to_csv(filePath, index_label='Date', date_format="%d-%m-%Y")

    rows = df.iloc[0 : df.shape[0]]
    data_rows = rows.to_json(orient='records')
    response_wrap = json.dumps({ "initialFileName": fileName, "generatedData" : data_rows })
    current_app.logger.info(response_wrap)
    return Response(response_wrap, mimetype='application/json')

@shapeConfigApi.route('/createCSV', methods=['POST'])
def createCSV():
    filePath = FILE_DIRECTORY + 'createTestFile.csv'
    df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                   'mask': ['red', 'purple'],
                   'weapon': ['sai', 'bo staff']})
    df.to_csv(filePath, index=False)
    rows = df.iloc[:]
    data_rows = rows.to_json(orient='records')
    return jsonify(data_rows)

@shapeConfigApi.route('/readCSV', methods=['POST'])
def readCSV():
    filePath = FILE_DIRECTORY + 'createTestFile.csv'
    df = pd.read_csv(filePath)
    rows = df.iloc[:]
    data_rows = rows.to_json(orient='records')
    return jsonify(data_rows)

@shapeConfigApi.route('/testlogs')
def testlog_route():
    """Default route"""
    current_app.logger.debug('testing logging api in shape -- DEBUG message')
    current_app.logger.info('testing logging api in shape -- INFO message')
    current_app.logger.warning('testing logging api in shape -- WARNING message')
    current_app.logger.error('testing logging api in shape -- ERROR message')
    current_app.logger.critical('testing logging api in shape --  CRITICAL message')
    return jsonify('testing api in shape -- hello world')