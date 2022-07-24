import requests
import asyncio
import aiohttp
from time import time
import json
import boto3
from . import trade_details_util
from . import trade_details
from . import config
from . import formula_details_util
from . import pricing_api_util
from . import constants as const
from . import platform_api_util
from ..valuationengine.kafka_util import Kafka_Producer

def run_valuation(headers, valuation_date):
    """Run valuation for a valuation date"""
    item_details = get_delivery_items_for_valuation(headers, valuation_date)

    # Getting price from AWS API
    # invoke_valuation_api_and_save_results(headers,valuation_date, item_details)
    # push_delivery_units_to_SQS(delivery_units)
    #invoke_valuation_for_item_details(headers, item_details)
    run_valuation_for_delivery_items_async(headers, item_details)
    #run_valuation_for_delivery_items_kafka(headers, item_details)
    return {"records_for_processing":item_details}


def get_delivery_items_for_valuation(headers, valuation_date):
    # get all contracts
    contract_details = trade_details_util._get_contracts(headers,["PW-88-REF"]) #trade_details_util._get_contract_all(headers)
    contract_dict = {contract[const.K_CONTRACT_NO] : contract for contract in contract_details}
    # get all items
    contract_ref_nos = trade_details_util.get_contract_ref_nos(
        contract_details)
    item_details = trade_details_util._get_contract_items(
        headers, contract_ref_nos)
    # get all formulas associated with contract & item
    formula_ids = trade_details_util.get_formula_ids(
        contract_details, item_details)
    formula_details = formula_details_util.get_formula_details(
        headers, formula_ids)
    formula_dict = {formula["_id"]: formula for formula in formula_details}

    # call pricing api to get price
    trade_details_util.populate_contract_info_in_item_details(
        item_details, contract_dict, formula_dict, valuation_date)

    return item_details


def invoke_valuation_api_and_save_results(headers, valuation_date, item_details):
    v_item_data, v_delivery_units_realized, v_delivery_units_unrealized = get_valuation_for_item_details(
        item_details, valuation_date)

    post_item_data_to_collection(headers, v_item_data)
    post_delivery_unit_to_collection(
        headers, v_delivery_units_realized, const.K_REALIZED)
    post_delivery_unit_to_collection(
        headers, v_delivery_units_unrealized, const.K_UNREALIZED)


def invoke_valuation_for_item_details(headers, item_details):
    delivery_units_realized = []
    delivery_units_unrealized = []
    item_data = []
    for item in item_details:
        result = get_delivery_unit_with_price_(headers, item)
        delivery_units_unrealized.extend(result["delivery_units_unrealized"])
        delivery_units_realized.extend(result["delivery_units_realized"])
        item_data.append(result["item_data"])
    print(item_data)
    return item_data, delivery_units_realized, delivery_units_unrealized


def post_item_data_to_collection(headers, item_data):
    collection_name = const.COLLECTION_NAME_ITEM
    collection_data = [
        list(item.values()) for item in item_data]
    platform_api_util.append_collection_data(
        headers, collection_name, collection_data)


def post_delivery_unit_to_collection(headers, delivery_units, REALIZED_UNREALIZED):
    collection_name = const.COLLECTION_NAME_DELIVERY_UNIT+"_"+REALIZED_UNREALIZED
    collection_data = [
        list(delivery_unit.values()) for delivery_unit in delivery_units]
    platform_api_util.append_collection_data(
        headers, collection_name, collection_data)


def get_delivery_unit_with_price_(headers, item):
    return pricing_api_util._post(headers, body=item)


def push_delivery_units_to_SQS(delivery_units):
    """Push delivery units to SQS Queue"""
    start = time()
    sqs = boto3.client('sqs')
    queue_url = config.SQS_QUEUE_URL

    for delivery_unit in delivery_units:
        delivery_unit_str = json.dumps(delivery_unit)
        sqs.send_message(QueueUrl=queue_url, MessageBody=delivery_unit_str)
    print("Push to Queue ", (time()-start))


def run_valuation_for_delivery_items_async(headers, delivery_items):
    #del headers["Authorization"]
    header_data = get_headers_data(headers)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coroutines = [invoke_valuation(header_data, item)
                  for item in delivery_items]
    loop.run_until_complete(asyncio.gather(*coroutines))


async def invoke_valuation(headers, delivery_unit):
    """"Call pricing api asynchronously"""
    print("Invoking valuation api for ", delivery_unit["powerItemRefNo"])
    #delivery_unit_str = json.dumps(delivery_unit, skipkeys=True)
    async with aiohttp.ClientSession() as session:
        async with session.post(config.VALUATION_API_URL, json=delivery_unit, headers=headers) as response:
            api_response = await response.json()
            return api_response

def run_valuation_for_delivery_items_kafka(headers, delivery_items):
    s = time()
    kafka_producer = Kafka_Producer()
    for item in delivery_items:
        payload = get_message_for_lambda(headers,item)
        kafka_producer.send(payload)
    print("time to send message to kafka ",(time()-s)*1000)

def get_message_for_lambda(headers,delivery_item):
    return {"params":{"header":get_headers_data(headers)},"body-json":delivery_item}

def get_headers_data(headers):
    return {
        "platform_host": headers["platform_host"],
        "platform_token": headers["platform_token"],
        "platform_url": headers["platform_url"]
    }
