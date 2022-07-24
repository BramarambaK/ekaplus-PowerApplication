import os
import requests
import sys
from . import config
from ..valuationengine.api_call_error import APICallError


def __get_connect_host():
    eka_connect_host = os.environ["eka_connect_host"]
    print("Connect api host ", eka_connect_host)
    return eka_connect_host


def _get(url, headers_data, params={}, body={}):
    """Method to make Connect Data API"""
    connect_host = __get_connect_host()
    url = f"{connect_host}/{url}"

    response = None
    #print(body)
    try:
        connect_response = requests.get(
            url, headers=headers_data, params=params, json=body)

        if connect_response.status_code == 200:
            response = connect_response.json()
        else:
            print(
                f"Error in getting details for {url} ", connect_response.json())
            raise APICallError(connect_response.json())
    except:
        print("Error in making API call", sys.exc_info()[0])
        raise APICallError("Error in making connect api call")
    return response


def form_filter_criteria(field_name=None, value_list=None, includes=None,excludes=None):
    filter_data = {}

    if field_name and value_list:
        filter_data["filterData"]={
            "filter": [
                        {
                            "fieldName": field_name,
                            "value": value_list,
                            "operator": "in"
                        }
            ]}

    if includes:
        filter_data["includeFields"] = includes
    if excludes:
        filter_data["excludeFields"] = excludes

    return filter_data
