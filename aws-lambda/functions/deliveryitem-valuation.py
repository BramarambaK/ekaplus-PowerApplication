import csv
import boto3
import json
from datetime import datetime, timedelta
from time import time
import pandas as pd
import os
import copy
import random
import sys
import requests
import traceback

BUCKET_NAME = os.environ['price_s3_bucket_name']
DATE_FORMAT = "%d-%m-%Y"
DATE_FORMAT_Month = "%d-%b-%Y"
TIME_FORMAT = "%H:%M"
MONTH_YEAR_FORMAT = "%b-%Y"

DELIVERY_ITEM_REQUIRED_KEYS = ["powerContractRefNo", "powerItemRefNo", "contractTypeDisplayName", "productDisplayName",
                               "traderNameDisplayName", "cpNameDisplayName", "dealTypeDisplayName", "paymentTermsDisplayName",
                               "taxScheduleCountryIdDisplayName", "taxScheduleIdDisplayName", "profitCenterDisplayName",
                               "facilityLocationDisplayName", "strategyDisplayName", "contractIssueDate", "deliveryTypeDisplayName",
                               "blockNo", "startTime", "endTime", "priceType", "quantity", "quantityUnitDisplayName",
                               "price", "priceUnitDisplayName", "marketPrice"]
PRICING_DELIVERY_ITEM_REQUIRED_KEYS = ["powerItemRefNo", "startTime", "endTime", "startDate", "endDate", "priceType", "priceUnit",
                                       "quantityUnit", "formulaDetails", "valuationFormulaDetails"]

K_VALUATION_RUN_DATE = "valuationRunDate"
K_DELIVERY_DATE = "deliveryDate"
K_START_TIME = "startTime"
K_END_TIME = "endTime"
K_PRICE_TYPE = "priceType"
K_FORMULA_EXP = "formulaExpression"
K_PRICE = "price"
K_DELIVERY_FREQ = "deliveryFrequency"
K_VALUATION_FORMULA_ID = "valuationFormulaId"
K_EXPRESSION = "expression"

COLLECTION_NAME_DELIVERY_UNIT = "Power_Exp_Del_Unit"
COLLECTION_NAME_DELIVERY_UNIT_DAILY = "Power_Exp_Daily_Del_Unit"
COLLECTION_NAME_ITEM = "Power_Exp_Item"
K_REALIZED = "RLZ"
K_UNREALIZED = "UNRLZ"
DELIVERY_TYPE_BLOCK = "Block"
DELIVERY_TYPE_SHAPE = "Shape"
PRICE_TYPE_FORMULA = "FormulaPricing"
PRICE_TYPE_FIXED = "Fixed"

lambda_client = boto3.client('lambda')
pricing_api_logical_resource_id = 'PricingLambdaFunction'
stack_name = os.environ.get('STACK_NAME')

def lambda_handler(event, context):
    result = {}
    headers = {}
    headers, item = get_data_from_event(event)
    print("Input Data  ", event)
    valuation_date = get_valuation_date(item)
    result = process_item(valuation_date, item)
    post_results_to_collection(headers, result)
    # post_item(headers)
    return result
    # return {"status": 200, "message": "Updated successfully"}

def get_physical_resource(logical_resource_id, stack_name):
    cfn_client = boto3.client('cloudformation', region_name='us-east-1')
    logger.info("Call to get the stack resources:")
    response = cfn_client.describe_stack_resources(StackName=stack_name, LogicalResourceId=logical_resource_id)
    logger.info("The stack resource to be invoked is:")
    logger.info(response)
    for i in response['StackResources']:
        if i['LogicalResourceId'] == logical_resource_id:
            physical_resource_id = i['PhysicalResourceId']
        else:
            logger.info("The stack does not have the child lambda function.")
            physical_resource_id = logical_resource_id
    logger.info(f"The physical resource id of the function to be invoked is : {physical_resource_id}")
    return physical_resource_id

def get_data_from_event(event):
    return event["headers"], event["body"]


def post_item(headers):
    collection_name = COLLECTION_NAME_ITEM
    collection_data = [["PW-2-REF", "PW-3-ITEM", "Purchase", "Gasoil", "admin eka", "24-7 Farms", "Third Party", "1 Day From Invoice Date", "No Tax - UK - Purchase", "Baltic Wheat",
                        "United Kingdom", "mumbai", "2018-19", "2020-05-08", "Block", 2, "00:00", "23:00", "FormulaPricing", 10, "MT", 9999.99, "USD/MT", 9999.99, "01-01-2020", "31-01-2020", "01-Jan-1970"]]
    append_collection_data(headers,
                           collection_name, collection_data)


def get_valuation_date(item):
    valuation_run_date = item[K_VALUATION_RUN_DATE]
    try:
        valuation_date = datetime.strptime(
            valuation_run_date, DATE_FORMAT_Month)
    except:
        print("Current Date is considered as Valuation Date")
        valuation_date = datetime.now()
    return valuation_date


def process_item(valuation_date, item):
    delivery_type = item["deliveryType"]
    price_type = item["priceType"]

    valuation_result = {}
    print("Getting delivery items - Start")
    if DELIVERY_TYPE_BLOCK == delivery_type or (DELIVERY_TYPE_SHAPE == delivery_type and PRICE_TYPE_FORMULA == price_type):
        delivery_items = get_delivery_item_block_both_shape_formula(
            valuation_date, item)
    else:
        delivery_items = get_delivery_item_shape_fixed(valuation_date, item)
    print("Getting delivery items - End")
    print("Getting prices for delivery items - Start")
    delivery_items_priced = get_delivery_item_price(delivery_items)
    print("Getting prices for delivery items - End")

    print("Getting valuation results data from delivery items")
    valuation_result = get_valuation_results(
        item, valuation_date, delivery_items_priced)
    print("Getting valuation results data from delivery items")

    return valuation_result


def get_delivery_item_block_both_shape_formula(valuation_date, item):
    """Valuation process for Block (Fixed & Formula) & Shape (Formula)"""
    delivery_items = []
    item_details = get_delivery_item_for_pricing(item)

    valuation_date_str = valuation_date.strftime(DATE_FORMAT)

    is_price_type_formula = False
    if item["priceType"] == "FormulaPricing":
        is_price_type_formula = True

    is_delivery_type_block = False
    if item["deliveryType"] == DELIVERY_TYPE_BLOCK:
        is_delivery_type_block = True

    if is_delivery_type_block:
        quantity_file_dir = item["fileDetails"]["quantity"]["bucketDir"]
        quantity_file = item["fileDetails"]["quantity"]["id"]
    else:
        # Shape
        quantity_file_dir = item["fileDetails"]["contracted"]["Quantity"]["bucketDir"]
        quantity_file = item["fileDetails"]["contracted"]["Quantity"]["id"]

    qty_df = load_file_to_dataframe(f"{quantity_file_dir}/{quantity_file}")

    if qty_df.empty:
        return
    columns = qty_df.columns.values
    column_count = len(columns)

    for row_tuple in qty_df.itertuples(index="True"):
        delivery_date_str = row_tuple[0]
        delivery_date = datetime.strptime(delivery_date_str, DATE_FORMAT)

        for i in range(1, column_count-1):
            qty = int(row_tuple[i])

            start_time = columns[i]
            if i < column_count:
                end_time = columns[i+1]
            else:
                # handle last column
                end_time = columns[i]

            delivery_item = get_delivery_item(
                valuation_date_str, delivery_date, start_time, end_time)
            delivery_item["quantity"] = qty

            # fixed price / formula price
            if is_delivery_type_block:
                delivery_item["contractPrice"] = item["price"]

            delivery_items.append(delivery_item)
    item_details["startDate"] = datetime.strptime(
        item_details["startDate"], DATE_FORMAT).strftime(DATE_FORMAT_Month)
    item_details["endDate"] = datetime.strptime(
        item_details["endDate"], DATE_FORMAT).strftime(DATE_FORMAT_Month)
    item_details["delivery_items"] = delivery_items
    return item_details


def get_delivery_item_shape_fixed(valuation_date, item):
    """Generate delivery item Shape fixed"""
    delivery_items = []
    item_details = get_delivery_item_for_pricing(item)

    valuation_date_str = valuation_date.strftime(DATE_FORMAT)
    # Shape
    quantity_file_dir = item["fileDetails"]["contracted"]["Quantity"]["bucketDir"]
    price_file_dir = item["fileDetails"]["contracted"]["Price"]["bucketDir"]
    quantity_file = item["fileDetails"]["contracted"]["Quantity"]["id"]
    price_file = item["fileDetails"]["contracted"]["Price"]["id"]

    qty_df = load_file_to_dataframe(f"{quantity_file_dir}/{quantity_file}")
    price_df = load_file_to_dataframe(f"{price_file_dir}/{price_file}")

    if qty_df.empty:
        return

    if price_df.empty:
        return

    columns = qty_df.columns.values
    column_count = len(columns)

    for qty_row_tuple, price_row_tuple in zip(qty_df.itertuples(index="True"), price_df.itertuples(index="True")):
        delivery_date_str = qty_row_tuple[0]
        delivery_date = datetime.strptime(delivery_date_str, DATE_FORMAT)

        for i in range(1, column_count-1):
            qty = int(qty_row_tuple[i])
            price = int(price_row_tuple[i])

            start_time = columns[i]
            if i < column_count:
                end_time = columns[i+1]
            else:
                # handle last column
                end_time = columns[i]

            delivery_item = get_delivery_item(
                valuation_date_str, delivery_date, start_time, end_time)

            delivery_item["quantity"] = qty
            delivery_item["contractPrice"] = price

            delivery_items.append(delivery_item)
    item_details["startDate"] = datetime.strptime(
        item_details["startDate"], DATE_FORMAT).strftime(DATE_FORMAT_Month)
    item_details["endDate"] = datetime.strptime(
        item_details["endDate"], DATE_FORMAT).strftime(DATE_FORMAT_Month)
    item_details["delivery_items"] = delivery_items
    return item_details


def load_file_to_dataframe(path):
    print("Loading delivery units from S3")
    data_frame = pd.DataFrame(columns=None)
    s3_client = boto3.client('s3')
    try:
        data_frame = pd.read_csv(s3_client.get_object(
            Bucket=BUCKET_NAME, Key=path)["Body"], index_col="Date")
    except Exception as exp:
        print("Error in getting data from s3 for ", path)
        print("Exception : ", sys.exc_info()[0], exp)
        traceback.print_exc()
    print("Loaded delivery units from S3")
    return data_frame


def get_default_delivery_item(item):
    default_delivery_unit = {key: (item[key] if key in item.keys() else "")
                             for key in DELIVERY_ITEM_REQUIRED_KEYS}
    return default_delivery_unit


def get_delivery_item_for_pricing(item):
    default_delivery_unit = {key: (item[key] if key in item.keys() else "")
                             for key in PRICING_DELIVERY_ITEM_REQUIRED_KEYS}
    return default_delivery_unit


def get_delivery_item(valuation_date, delivery_date, start_time, end_time):

    delivery_item = {}
    delivery_item[K_DELIVERY_DATE] = delivery_date.strftime(
        DATE_FORMAT)
    delivery_item[K_START_TIME] = start_time
    delivery_item[K_END_TIME] = end_time
    delivery_item["asOfDate"] = valuation_date

    return delivery_item


def post_results_to_collection(headers, result):
    print("Saving results in platform collection")
    v_item_data = result["item_details"]

    post_item_data_to_collection(headers, v_item_data)
    post_delivery_unit_to_collection(
        headers, result["delivery_units_realized"], COLLECTION_NAME_DELIVERY_UNIT, K_REALIZED)
    post_delivery_unit_to_collection(
        headers, result["delivery_units_unrealized"], COLLECTION_NAME_DELIVERY_UNIT, K_UNREALIZED)
    post_delivery_unit_to_collection(
        headers, result["daily_realized"], COLLECTION_NAME_DELIVERY_UNIT_DAILY, K_REALIZED)
    post_delivery_unit_to_collection(
        headers, result["daily_unrealized"], COLLECTION_NAME_DELIVERY_UNIT_DAILY, K_UNREALIZED)
    print("Results saved in platform collection")


def post_item_data_to_collection(headers, item_data):
    collection_name = COLLECTION_NAME_ITEM
    collection_data = []
    collection_data.append(list(item_data.values()))
    append_collection_data(headers,
                           collection_name, collection_data)


def post_delivery_unit_to_collection(headers, delivery_units, collection_name_, REALIZED_UNREALIZED):
    collection_name = collection_name_+"_"+REALIZED_UNREALIZED
    collection_data = [
        list(delivery_unit.values()) for delivery_unit in delivery_units]
    append_collection_data(headers,
                           collection_name, collection_data)


def append_collection_data(headers, collection_name, collection_data):
    platform_url = headers["platform_url"]
    headers_data = {
        "Host": headers["platform_host"],
        "Authorization": headers["platform_token"],
        "Content-Type": "application/json",

    }
    url = f"{platform_url}/collection/v1/append/data"

    response = None
    payload = {
        "collectionName": collection_name,
        "collectionData": collection_data
    }
    # print(payload)
    try:
        connect_response = requests.put(
            url, headers=headers_data, json=payload)

        if connect_response.status_code == 200:
            response = connect_response.json()
        else:
            print(
                f"Error in getting details for {url} ", connect_response.json())

    except ConnectionError as conn_error:
        print("Connection error ", conn_error)
    except:
        print("Error in posting data to collection ", sys.exc_info()[0])
        traceback.print_exc()

    return response


def get_delivery_item_price(payload):
    print("Pricing payload ", payload)
	physical_resource_id = get_physical_resource(pricing_api_logical_resource_id, stack_name)
	
    response = lambda_client.invoke(
        FunctionName=physical_resource_id,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload),
    )
    price_data = json.loads(response["Payload"].read())
    return price_data


def get_valuation_results(item, valuation_date, delivery_items_priced):
    default_delivery_item = get_default_delivery_item(item)

    delivery_items_realized = []
    delivery_items_unrealized = []
    daily_realized = []
    daily_unrealized = []
    item_details = {}
    valuation_result = {
        "delivery_units_realized": delivery_items_realized,
        "delivery_units_unrealized": delivery_items_unrealized,
        "daily_realized": daily_realized,
        "daily_unrealized": daily_unrealized,
        "item_details": item_details
    }

    delivery_items = delivery_items_priced["delivery_items"]
    valuation_date_str = item["valuationRunDate"]
    item_start_date = item["startDate"]
    item_end_date = item["endDate"]
    item_start_time = item["startTime"]
    item_end_time = item["endTime"]

    total_item_price = 0
    # lowest level - hourly/minutely
    for delivery_item in delivery_items:
        del_item = copy.deepcopy(default_delivery_item)
        delivery_date_str = delivery_item["deliveryDate"]
        delivery_date = datetime.strptime(delivery_date_str, DATE_FORMAT)

        del_item["price"] = delivery_item["contractPrice"]
        del_item["marketPrice"] = delivery_item["marketPrice"]
        del_item["startTime"] = delivery_item["startTime"]
        del_item["endTime"] = delivery_item["endTime"]
        del_item["deliveryDate"] = delivery_date_str
        del_item["periodEndDate"] = valuation_date_str

        if delivery_date < valuation_date:
            delivery_items_realized.append(del_item)
        else:
            delivery_items_unrealized.append(del_item)
    # daily
    daily_delivery_items = get_daily_delivery_items(delivery_items)
    for delivery_item in daily_delivery_items:
        del_item = copy.deepcopy(default_delivery_item)
        delivery_date_str = delivery_item["deliveryDate"]
        delivery_date = datetime.strptime(delivery_date_str, DATE_FORMAT)

        del_item["price"] = delivery_item["contractPrice"]
        del_item["marketPrice"] = delivery_item["marketPrice"]
        del_item["startTime"] = item_start_time
        del_item["endTime"] = item_end_time
        del_item["startDate"] = item_start_date
        del_item["endDate"] = item_end_date
        del_item["periodEndDate"] = valuation_date_str

        if delivery_date < valuation_date:
            daily_realized.append(del_item)
        else:
            daily_unrealized.append(del_item)

    item_details = copy.deepcopy(default_delivery_item)
    contractPrice, marketPrice = get_item_price(daily_delivery_items)
    item_details["price"] = contractPrice
    item_details["marketPrice"] = marketPrice

    item_details["startDate"] = item_start_date
    item_details["endDate"] = item_end_date
    item_details["periodEndDate"] = valuation_date_str
    valuation_result["item_details"] = item_details

    return valuation_result


def get_daily_delivery_items(delivery_items):
    del_item_df = pd.DataFrame(delivery_items)
    d = del_item_df.groupby('deliveryDate', as_index=False).sum()
    return d.to_dict(orient="records")


def get_item_price(daily_delivery_items):
    del_item_df = pd.DataFrame(daily_delivery_items)
    contractPrice = del_item_df["contractPrice"].sum()
    marketPrice = del_item_df["marketPrice"].sum()
    return contractPrice, marketPrice
