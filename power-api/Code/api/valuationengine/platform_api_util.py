import os
import requests
import sys
import json
from . import config
from ..valuationengine.api_call_error import APICallError
from . import constants as const


def post_collection_data(headers_data, collection_name, collection_data):
    platform_url = config.PLATFORM_URL
    url = f"{platform_url}/collection/v1"

    response = None
    payload = get_api_payload(collection_name, collection_data)
    # print(payload)
    try:
        connect_response = requests.post(
            url, headers=headers_data, json=payload)

        if connect_response.status_code == 200:
            response = connect_response.json()
        else:
            print(
                f"Error in getting details for {url} ", connect_response.json())
            raise APICallError(connect_response.json())
    except:
        print("Error in making API call", sys.exc_info()[0])
        raise APICallError("Error in making platform api call")
    return response

def append_collection_data(headers_data, collection_name, collection_data):
    platform_url = config.PLATFORM_URL
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
            raise APICallError(connect_response.json())
    except:
        print("Error in making API call", sys.exc_info()[0])
        raise APICallError("Error in making platform api call")
    return response

def get_api_payload(collection_name, collection_data):
    collection_header = get_collection_header(collection_name)
    payload = {
        "collectionName": collection_name,
        "collectionDescription": collection_name,
        "dataLoadOption": "replace",
        "collectionHeader": collection_header,
        "collectionData": collection_data
    }
    return payload


def get_collection_header(collection_name):
    file = "collection_item_header.json"
    if const.COLLECTION_NAME_DELIVERY_UNIT in collection_name:
        file = "collection_delivery_unit_header.json"

    with open(file) as collection_header_file:
        collection_header = json.load(collection_header_file)
    return collection_header


if __name__ == "__main__":
    print(get_collection_header(const.COLLECTION_NAME_DELIVERY_UNIT+const.K_UNREALIZED))
