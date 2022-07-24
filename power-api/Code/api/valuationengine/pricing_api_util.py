import os
import requests
import sys
from . import config
from ..valuationengine.api_call_error import APICallError


def _post(headers=None, params={}, body={}):
    """Method to make Pricing API call"""
    response = None
    url = config.VALUATION_API_URL
    headers_data = {
        "platform_host": headers["platform_host"],
        "platform_token": headers["platform_token"],
        "platform_url": headers["platform_url"]
    }
    print(url)
    print(body)
    print(headers_data)
    try:
        api_response = requests.post(
            url, headers=headers_data,  json=body)

        if api_response.status_code == 200:
            response = api_response.json()
        else:
            print(
                f"Error in getting details for {url} ", api_response.json())
            raise APICallError(api_response.json())
    except:
        print("Error in making API call", sys.exc_info()[0])
        raise APICallError("Error in making pricing api call")
    return response


if __name__ == "__main__":
    body = {
        "powerContractRefNo": "PW-14-REF",
        "quantityUnitDisplayName": "MT",
        "payInCurIdDisplayName": "CAD",
        "blockNo": 1,
        "price": 200,
        "quantity": 200,
        "expression": "5eaf6b1de21b840001c59ce6",
        "priceType": "FormulaPricing",
        "powerItemRefNo": "PW-7-ITEM",
        "priceUnitDisplayName": "USD/BBL",
        "deliveryDate": "22-01-2020",
        "startTime": "13:00",
        "endTime": "14:00",
        "formulaDetails": {
            "includedCurves": [
                "NYMEX Light Sweet Crude Oil(WTI) Futures"
            ]
        }
    }
    print(_post(body=body))
