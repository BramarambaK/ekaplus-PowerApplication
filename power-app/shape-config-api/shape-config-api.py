from flask import Flask, request, jsonify
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

app = Flask(__name__)
app.config.from_pyfile('config_shape.cfg')

EKA_UTILITY_HOST = os.environ.get('eka_utility_host')
#EKA_UTILITY_HOST = 'http://192.168.1.225:7073'

df_combined = pd.DataFrame(np.zeros((0,0)))

@app.route('/shape/file', methods=['POST'])
def get_file():
    req_data = request.get_json()
    req_headers = dict(request.headers)
    if req_data['dropdown'] == 'All':
        Quantity_fileName = checkAndDownloadFile(req_data['fileDetails']['Quantity'], req_headers)
        Price_fileName =  checkAndDownloadFile(req_data['fileDetails']['Price'], req_headers)
        df_quality = pd.read_csv(Quantity_fileName, encoding = "ISO-8859-1", parse_dates=['Date'])
        df_price = pd.read_csv(Price_fileName, encoding = "ISO-8859-1", parse_dates=['Date'])
        cols = list(df_quality.columns)
        cols.pop(0)
        global df_combined
        df_combined['Date'] = df_quality['Date'].dt.strftime("%d-%m-%Y")
        for col in cols:
            df_combined[col] = df_quality[col].map(str) + '  |  ' + df_price[col].map(str)    
        return {'msg': 'file combined successfully'}
    else :
        dropdown = req_data['dropdown']
        fileName = checkAndDownloadFile(req_data['fileDetails'][dropdown], req_headers)
        df = pd.read_csv(fileName, encoding = "ISO-8859-1")
        print(fileName)
        return {'msg': 'file fetched successfully'}

def checkAndDownloadFile(fileDetails, req_headers):
    if os.path.exists(fileDetails['fileName']):
        return fileDetails['fileName']
    if fileDetails['id']:
        headers = getFileAPI_headers(req_headers)
        headers["storageType"] = "awsS3"
        headers["folderInS3"] = "powerDocs"
        body = getFileAPI_body(fileDetails)
        resp = requests.post(EKA_UTILITY_HOST + '/download', json = body, headers = headers)
        print(fileDetails['fileName'])
        f = open(fileDetails['fileName'], "wb")
        f.write(resp.content)
        f.close()
        return fileDetails['fileName']


@app.route('/shape/columns', methods=['POST'])
def get_columns():
    req_data = request.get_json()
    fileName = req_data['fileName']
    if fileName == 'All':
        cols = list(df_combined.columns)
        response_wrap = { "columns" : cols }
        result = response_wrap
        print(result)
        return result
    else:
        df = pd.read_csv(fileName, encoding = "ISO-8859-1")
        cols = list(df.columns)
        response_wrap = { "columns" : cols }
        result = response_wrap
        print(result)
        return result 

@app.route('/shape/data', methods=['POST'])
def get_rows():
    req_data = request.get_json()
    startingRow = int(req_data['startingRow'])
    endingRow = startingRow + 100
    fileName = req_data['fileName']
    startDate = req_data['startDate'].split()
    endDate = req_data['endDate']
    if fileName == 'All':
        print(df_combined.head(5))
        rows = df_combined.iloc[startingRow : endingRow]
        data_rows = rows.to_json(orient='records')
        response_wrap = { "rows" : data_rows }
        print(response_wrap)
        return response_wrap
    else:
        mydateparser = lambda x: pd.to_datetime(x, dayfirst=True)
        df = pd.read_csv(fileName, encoding = "ISO-8859-1", parse_dates=['Date'], date_parser=mydateparser)
        df['Date'] = df['Date'].dt.strftime("%d-%m-%Y")
        rows = df.iloc[startingRow : endingRow]
        data_rows = rows.to_json(orient='records')
        response_wrap = { "rows" : data_rows }
        print(response_wrap)
        return response_wrap

@app.route('/shape/update', methods=['POST'])
def update_value():
    req_data = request.get_json()
    rowIndex = int(req_data['rowIndex'])
    colIndex = int(req_data['colIndex'])

    if req_data['attribute'] == 'All':
        Quantity = req_data['Quantity']
        Price = req_data['Price']

        Quantity_file = req_data['Quantity_file']
        df1 = pd.read_csv(Quantity_file, encoding = "ISO-8859-1")
        df1.iloc[rowIndex,colIndex] = req_data['Quantity']
        df1.to_csv(Quantity_file, index=False, date_format="%d-%m-%Y")

        Price_file = req_data['Price_file']
        df2 = pd.read_csv(Price_file, encoding = "ISO-8859-1")
        df2.iloc[rowIndex,colIndex] = req_data['Price']
        df2.to_csv(Price_file, index=False, date_format="%d-%m-%Y")

        msg = 'row {} col {} , File {} with Quanity {} and File {} with Price {}'.format(rowIndex,colIndex,Quantity_file,Quantity,Price_file,Price)
        return {'msg': msg}
    else :
        value = req_data['value']
        fileName = req_data['fileName']
        df = pd.read_csv(fileName, encoding = "ISO-8859-1")
        df.iloc[rowIndex,colIndex] = value
        df.to_csv(fileName, index=False, date_format="%d-%m-%Y")
  
        msg = 'row {} col {} of File {} update with {}'.format(rowIndex,colIndex,fileName,value)
        return {'msg': msg}

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

@app.route('/filedownload', methods=['POST'])
def file_download():
    req_data = request.get_json()
    req_headers = dict(request.headers)
    req_body = dict(req_data)

    new_fileName = req_body['id'] + ".csv"

    headers = getFileAPI_headers(req_headers)
    body = getFileAPI_body(req_body)

    resp = requests.post(EKA_UTILITY_HOST + '/download', json = body, headers = headers)
    print(new_fileName)
    f = open(new_fileName, "wb")
    f.write(resp.content)
    f.close()
    
    startDate = reverseDate(req_body["startDate"])
    endDate = reverseDate(req_body["endDate"])
    mydateparser = lambda x: pd.to_datetime(x, dayfirst=True)
    df = pd.read_csv(new_fileName, encoding = "ISO-8859-1", parse_dates=['Date'], date_parser=mydateparser, index_col="Date")
    displayRange = df[startDate:endDate]
    displayRange.to_csv(new_fileName, date_format="%d-%m-%Y")

    validity = {}
    if req_data['timeFrequency']:
        validity = testValidateColumnFreq(new_fileName, req_data['timeFrequency'])
    else:
        validity = {'validity': False, 'msg' : 'timeFrequency not present in payload'}

    return {'fileName': new_fileName, 'timeFrequencyValidity': validity}

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

@app.route('/shape/validate', methods=['POST'])
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
        df = pd.read_csv(fileName, encoding = "ISO-8859-1", parse_dates=["Date"],date_parser=mydateparser, index_col="Date")
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

@app.route('/shape/fileUpload', methods=['POST'])
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
                print("======== updated file =======")
                print(response_obj)
            else:
                response_obj[tabName][attribute] = uploadFile(fileMeta)
                print("********* uploaded new file ********")
                print(response_obj)
    return response_obj

@app.route('/shape/copyFile', methods=['POST'])
def copyFile():
    req_data = request.get_json()
    fileName = req_data['copy_from']['fileName']
    df = pd.read_csv(fileName, encoding = "ISO-8859-1")
    new_fileName = fileName + req_data['copy_to']['tab'] + req_data['copy_to']['dropdown'] + '.csv'
    df.to_csv(new_fileName, index=False, date_format="%d-%m-%Y")
    return { 'fileName' : new_fileName, 'tab': req_data['copy_to']['tab'] , 'dropdown': req_data['copy_to']['dropdown'] }


@app.route('/shape/resetToContracted', methods=['POST'])
def resetToContracted():
    req_data = request.get_json()
    fileName = req_data['fileName']
    df = pd.read_csv(fileName, encoding = "ISO-8859-1")
    if fileName == 'All':
        cols = list(df_combined.columns)
        response_wrap = { "columns" : cols }
        result = response_wrap
        print(result)
        return result
    else:
        df = pd.read_csv(fileName, encoding = "ISO-8859-1")
        cols = list(df.columns)
        response_wrap = { "columns" : cols }
        result = response_wrap
        print(result)
        return result 

@app.route('/block/blockToExcel', methods=['POST'])
def blockToExcel():
    req_data = request.get_json()
    req_headers = dict(request.headers)
    response_obj = {}
    blockDetails = json.loads(req_data['blockDetails'])
    for block in blockDetails:
        print(block)
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
        print(freqNeeded)
        
        dateRange = pd.DatetimeIndex([])
        print(dateRange)
        for freqDay in freqNeeded:
            print(freqDay)
            dayRange = pd.date_range(startDate, endDate, freq=freqDay)
            dateRange = dateRange.append(dayRange)
        dateRange = dateRange.sort_values()
        print(dateRange)

        cols = ["00:00","1:00","2:00","3:00","4:00","5:00","6:00","7:00","8:00","9:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"]
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

    print("the result is")
    response = response_obj
    print(response)
    return response

def createFile(df, block, fileName, req_headers, attribute):
    response_obj = {}
    df.index.name = 'Date'
    df.to_csv(fileName, date_format="%d-%m-%Y")
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
    headers = {
        "Authorization": fileMeta['Authorization'],
        "X-TenantID": fileMeta['X-Tenantid'],
        "storageType":"awsS3",
        "folderInS3" : "powerDocs"
    }
    files = {
        "file": (fileMeta['fileName'], open(fileMeta['fileName'], 'rb'), 'text/plain'),
        "description": (None, fileMeta['description']),
        "refObjectId": (None, "9c86d836-36e7-41f1-bb6f-71efd7df43aa"),
        "refObject": (None, "power"),
    }
    resp = requests.post(EKA_UTILITY_HOST + '/upload',files=files,headers=headers)
    upload_response = json.loads(resp.text)
    return upload_response

def updateFile(fileMeta):
    req_data = request.get_json()
    req_headers = dict(request.headers)
    headers = {
        "Authorization": fileMeta['Authorization'],
        "X-TenantID": fileMeta['X-Tenantid'],
        "storageType":"awsS3",
        "folderInS3" : "powerDocs"
    }
    files = {
        "file": (fileMeta['fileName'], open(fileMeta['fileName'], 'rb'), 'text/plain'),
        "description": (None, fileMeta['description']),
        "refObjectId": (None, "9c86d836-36e7-41f1-bb6f-71efd7df43aa"),
        "refObject": (None, "power"),
        "fileId" : (None, fileMeta['fileId'])
    }
    resp = requests.post(EKA_UTILITY_HOST + '/update',files=files,headers=headers)
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
    print('frequency time list :')
    print(timeList)
    return timeList

def validateColumnFrequency(freq, columns):
    timeList = getTimeFrequencyList(freq)
    print('The excel column values are:')
    print(columns.values)
    print('The validity is as follows:')
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
    df = pd.read_csv(fileName, encoding = "ISO-8859-1", parse_dates=['Date'], date_parser=mydateparser)
    df.pop('Date')
    result = validateColumnFrequency(freq, df.columns)
    print(result)
    return result

@app.route('/testPythonAPI', methods=['POST'])
def testAPI():
    print('json dumps')
    test = json.dumps({'working': 'API is working'})
    print(test)
    print(type(test))
    print('normal')
    test2 = {'working': 'API is working'}
    print(test2)
    print(type(test2))
    return test2

@app.route('/shape/createInitialShapeFile', methods=['POST'])
def createInitailShapeFile():
    shapeDetails = request.get_json()
    print(shapeDetails)
    startDate = getRngDate(shapeDetails['startDate'])
    endDate = getRngDate(shapeDetails['endDate'])
    timeFrequency = shapeDetails['timeFrequency']
    generatedFrequency = getTimeFrequencyList(timeFrequency)
    print(generatedFrequency)

    dateRange = pd.DatetimeIndex([])
    dateRange = pd.date_range(startDate, endDate)
    dateRange = dateRange.sort_values()
    print(dateRange)

    df = pd.DataFrame(0,columns=generatedFrequency, index=dateRange)
    print(df)
    fileName = 'shape_' + str(shapeDetails['blockNo']) + '_' + str(random.randint(1, 10000000)) + '.csv'
    df.to_csv(fileName, index_label='Date', date_format="%d-%m-%Y")

    rows = df.iloc[0 : df.shape[0]]
    data_rows = rows.to_json(orient='records')
    response_wrap = { "initialFileName": fileName, "generatedData" : data_rows }
    print(response_wrap)
    return response_wrap

if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
