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
                                       "quantityUnit", "formulaDetails"]

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

DELIVERY_TYPE_BLOCK = "Block"
DELIVERY_TYPE_SHAPE = "Shape"
PRICE_TYPE_FORMULA = "FormulaPricing"
PRICE_TYPE_FIXED = "Fixed"

lambda_client = boto3.client('lambda')

pricing_api_logical_resource_id = 'PricingLambdaFunction'
stack_name = os.environ.get('STACK_NAME')

def lambda_handler(event, context):
    result = {}
    headers, item = get_data_from_event(event)
    result = process_item(item)
    return result
	
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
    input_body = event["body"]
    input_body = input_body.rstrip('\r\n')
    input_body = json.loads(input_body)
    return event["headers"], input_body


def process_item(item):
    print("PROCESSING ITEM FOR CONTRACT PRICE ")
    delivery_type = item["deliveryType"]
    price_type = item["priceType"]

    if DELIVERY_TYPE_BLOCK == delivery_type or (DELIVERY_TYPE_SHAPE == delivery_type and PRICE_TYPE_FORMULA == price_type):
        delivery_items = get_delivery_item_block_both_shape_formula(
            item)
    else:
        delivery_items = get_delivery_item_shape_fixed(item)

    delivery_items_priced = get_delivery_item_price(delivery_items)
    print("PROCESSING ITEM FOR CONTRACT PRICE - COMPLETED")
    return delivery_items_priced


def get_delivery_item_block_both_shape_formula(item):
    """Valuation process for Block (Fixed & Formula) & Shape (Formula)"""
    print("GETTING DELIVERY ITEMS FOR FORMULA PRICE TYPE")
    delivery_items = []
    item_details = get_delivery_item_for_pricing(item)

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
                delivery_date, start_time, end_time)
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
    item_details["valuationFormulaDetails"]={}
    print("GETTING DELIVERY ITEMS FOR FORMULA PRICE TYPE - COMPLETED")
    return item_details


def get_delivery_item_shape_fixed(item):
    """Generate delivery item Shape fixed"""
    print("GETTING DELIVERY ITEMS FOR SHAPE FIXED PRICE TYPE")
    delivery_items = []
    item_details = get_delivery_item_for_pricing(item)

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
    
    print("COLUMNS ",columns)

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
                delivery_date, start_time, end_time)

            delivery_item["quantity"] = qty
            delivery_item["contractPrice"] = price

            delivery_items.append(delivery_item)
    item_details["startDate"] = datetime.strptime(
        item_details["startDate"], DATE_FORMAT).strftime(DATE_FORMAT_Month)
    item_details["endDate"] = datetime.strptime(
        item_details["endDate"], DATE_FORMAT).strftime(DATE_FORMAT_Month)
    item_details["delivery_items"] = delivery_items
    item_details["valuationFormulaDetails"]={}
    print("GETTING DELIVERY ITEMS FOR SHAPE FIXED PRICE TYPE - COMPLETED")
    return item_details


def load_file_to_dataframe(path):
    print("LOADING DELIVERY DETAILS FROM S3 ")
    data_frame = pd.DataFrame(columns=None)
    s3_client = boto3.client('s3')
    try:
        data_frame = pd.read_csv(s3_client.get_object(
            Bucket=BUCKET_NAME, Key=path)["Body"], index_col="Date")
    except:
        print("Exception : ", sys.exc_info()[0])
        print("Error in getting data from s3 for ", path)

    print("LOADING DELIVERY DETAILS FROM S3 - COMPLETED")    
    return data_frame


def get_default_delivery_item(item):
    default_delivery_unit = {key: (item[key] if key in item.keys() else "")
                             for key in DELIVERY_ITEM_REQUIRED_KEYS}
    return default_delivery_unit


def get_delivery_item_for_pricing(item):
    default_delivery_unit = {key: (item[key] if key in item.keys() else "")
                             for key in PRICING_DELIVERY_ITEM_REQUIRED_KEYS}
    return default_delivery_unit


def get_delivery_item(delivery_date, start_time, end_time):

    delivery_item = {}
    delivery_item[K_DELIVERY_DATE] = delivery_date.strftime(
        DATE_FORMAT)
    delivery_item[K_START_TIME] = start_time
    delivery_item[K_END_TIME] = end_time

    return delivery_item


def get_delivery_item_price(payload):
    print("PRICE PAYLOAD ",payload)
	physical_resource_id = get_physical_resource(pricing_api_logical_resource_id, stack_name)
    response = lambda_client.invoke(
        FunctionName=physical_resource_id,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload),
    )
    return json.loads(response["Payload"].read())


def get_daily_delivery_items(delivery_items):
    del_item_df = pd.DataFrame(delivery_items)
    d = del_item_df.groupby('deliveryDate', as_index=False).sum()
    return d.to_dict(orient="records")


def get_item_price(daily_delivery_items):
    del_item_df = pd.DataFrame(daily_delivery_items)
    contractPrice = del_item_df["contractPrice"].sum()
    return contractPrice
